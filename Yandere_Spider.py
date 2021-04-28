import urllib.request
import urllib.parse
import requests
import re
from bs4 import BeautifulSoup
from Mylog import Mylog as mylog
from UserAgent import UserAgent
import codecs
from pathlib import Path
import threading
import time
import random
import os

# 图片信息
class Yandere_Pic_Info(object):
	url = None
	score = None
	id = None
	tags = None
	length = None
	width = None
	author = None
	source = None
	md5 = None
	rating = None


# 获得下载要求
class Download_Requirements(object):
	def __init__(self):
		self.keyword_Num = 1		# 关键词数量
		self.keyword = None			# 第一个关键词
		self.extra_Keyword = []		# 更多的关键词
		self.filtered_Keyword_Num = 0			# 屏蔽的关键词数量
		self.filtered_Keyword = []	# 屏蔽的关键词
		self.start_Page = 1			# 开始页码
		self.max_Page = 0			# 结束页码，0代表自动获取最大页码
		self.delay_Time = -10		# 爬虫间隔
		self.thread_Num = 5			# 线程数量
		self.min_Score = 0			# 爬取图片评分最低值
		self.rating = [True, True, True]		# 爬取图片分级
		self.download_Path = None	# 存储路径
		self.start_URL = None		# 下载页面起始路径（由信息自动生成）

	def Get_Requirements(self):
		test_Character = str(input('是否使用文件中已有预设？(Y/N): '))
		if test_Character == 'Y' or test_Character == 'y': # 使用文件中预设
			file_Name = str(input('请输入预设文件名: '))
			file = open(file_Name, 'r')
			file_Content = file.read().split('\n')
			self.keyword_Num = int(file_Content[0])
			self.keyword = file_Content[1]
			if self.keyword_Num > 1:
				for i in range(0, self.keyword_Num - 1):
					self.extra_Keyword.append(file_Content[i + 2])
			self.filtered_Keyword_Num = int(file_Content[self.keyword_Num + 1])
			if self.filtered_Keyword_Num > 1:
				for i in range(0, self.filtered_Keyword_Num):
					self.filtered_Keyword.append(file_Content[self.keyword_Num + 2 + i])
			self.download_Path = file_Content[self.keyword_Num + self.filtered_Keyword_Num + 2]
			self.start_Page = int(file_Content[self.keyword_Num + self.filtered_Keyword_Num + 3])
			self.max_Page = int(file_Content[self.keyword_Num + self.filtered_Keyword_Num + 4])
			self.delay_Time = int(file_Content[self.keyword_Num + self.filtered_Keyword_Num + 5])
			self.thread_Num = int(file_Content[self.keyword_Num + self.filtered_Keyword_Num + 6])
			self.min_Score = int(file_Content[self.keyword_Num + self.filtered_Keyword_Num + 7])
			test_Character = file_Content[self.keyword_Num + self.filtered_Keyword_Num + 8]
			if test_Character != '':
				self.rating[0] = (test_Character[0] == '1')
				self.rating[1] = (test_Character[1] == '1')
				self.rating[2] = (test_Character[2] == '1')
		else: # 使用自定义输入预设
			# 获得关键词数量
			test_Character = str(input('请输入关键词数量（默认为1）: ')) # 用于检测输入是否为空
			if test_Character != '':
				self.keyword_Num = int(test_Character)
			# 获得关键词
			if self.keyword_Num == 1:
				self.keyword = str(input('请输入关键词 <不能为空！>: '))
			else:
				self.keyword = str(input('请输入关键词 <不能为空！>: \n'))
				for i in range(0, self.keyword_Num - 1):
					self.extra_Keyword.append(str(input()))
			# 获得屏蔽关键词数量
			test_Character = str(input('请输入需屏蔽的关键词数量（默认为0）: ')) # 用于检测输入是否为空
			if test_Character != '':
				self.filtered_Keyword_Num = int(test_Character)
			# 获得屏蔽关键词
			if self.filtered_Keyword_Num == 1:
				self.filtered_Keyword.append(str(input('请输入需屏蔽的关键词 <不能为空！>: ')))
			elif self.filtered_Keyword_Num > 1:
				self.filtered_Keyword.append(str(input('请输入需屏蔽的关键词 <不能为空！>: \n')))
				for i in range(0, self.filtered_Keyword_Num - 1):
					self.filtered_Keyword.append(str(input()))
			# 获得存储路径
			self.download_Path = str(input('请输入存储路径 <不能为空！>: '))
			# 获得起始页码
			test_Character = str(input('请输入起始页码（相对于第一个关键词，默认为1）: ')) # 用于检测输入是否为空
			if test_Character != '':
				self.start_Page = int(test_Character)
			# 获得结束页码
			test_Character = str(input('请输入结束页码（相对于第一个关键词，默认为0，即自动获取最大页码）: ')) # 用于检测输入是否为空
			if test_Character != '':
				self.max_Page = int(test_Character)
				if self.max_Page < self.start_Page:
					self.max_Page = 0
			# 获得爬虫间隔
			test_Character = str(input('请输入爬取时间间隔（单位：s）（默认为-10，-n代表在0到n间产生一个随机数）: ')) # 用于检测输入是否为空
			if test_Character != '':
				self.delay_Time = int(test_Character)
			# 获得线程数量
			test_Character = str(input('请输入线程数量（默认为5）: ')) # 用于检测输入是否为空
			if test_Character != '':
				self.thread_Num = int(test_Character)
			# 获得爬取评分最低值
			test_Character = str(input('请输入爬取评分最低值（默认为0）: ')) # 用于检测输入是否为空
			if test_Character != '':
				self.min_Score = int(test_Character)
			# 获得爬取分级
			test_Character = str(input('请输入爬取分级（输入三个连续的0或1，如011，分别代表safe、questionable和explicit）（默认为111）: '))
			if test_Character != '':
				self.rating[0] = (test_Character[0] == '1')
				self.rating[1] = (test_Character[1] == '1')
				self.rating[2] = (test_Character[2] == '1')

		# 处理关键词，字母小写+替换空格
		self.keyword = self.keyword.lower().replace(' ','_')
		for i in range(0, len(self.extra_Keyword)):
			self.extra_Keyword[i] = self.extra_Keyword[i].lower().replace(' ','_')			
		for i in range(0, len(self.filtered_Keyword)):
			self.filtered_Keyword[i] = self.filtered_Keyword[i].lower().replace(' ','_')		

		if self.download_Path[-1] != '\\':
			self.download_Path = self.download_Path + '\\'
		self.start_URL = 'https://yande.re/post?page=' + str(self.start_Page) + '&tags=' + urllib.parse.quote(self.keyword)

	def Output_Info(self): # 返回当前爬取要求信息的字符串，可用于写入日志或检查
		output_Str = ''

		if self.keyword_Num == 1:
			output_Str += '\r\n关键词: ' + str(self.keyword)
		else:
			output_Str += '\r\n关键词: \r\n' + str(self.keyword)
			for kw in self.extra_Keyword:
				output_Str += '\r\n' + kw
		
		if self.filtered_Keyword_Num == 1:
			output_Str += '\r\n需屏蔽的关键词: ' + str(self.filtered_Keyword[0])
		elif self.filtered_Keyword_Num > 1:
			output_Str += '\r\n需屏蔽的关键词:'
			for kw in self.filtered_Keyword:
				output_Str += '\r\n' + kw

		output_Str = output_Str\
				   + '\r\n起始页码: ' + str(self.start_Page)\
				   + '\r\n结束页码: ' + str(self.max_Page)\
				   + '\r\n爬取时间间隔: ' + str(self.delay_Time)\
				   + '\r\n线程数量: ' + str(self.thread_Num)\
				   + '\r\n爬取评分最低值: ' + str(self.min_Score)\
				   + '\r\n爬取分级: ' + 'Safe: ' + str(self.rating[0]) + ' | Questionable: ' + str(self.rating[1]) + ' | Explicit: ' + str(self.rating[2])\
				   + '\r\n存储路径: ' + str(self.download_Path)\
				   + '\r\n起始爬取URL: ' + str(self.start_URL) + '\r\n'
		return output_Str



class Yandere_InfoLink_Download(object):
	def __init__(self, download_requirements):
		self.spider_info = download_requirements
		self.log = mylog()

		print('\n正在测试连接...')
		htmlContent = self.getResponseContent(download_requirements.start_URL) # 先进行一次访问，测试能否连接
		if htmlContent == None:
			self.log.critical('连接: yande.re 失败。程序结束。')
			print('yande.re访问失败。请检查网络连接。')
			return
		else:
			self.log.info('连接: yande.re 成功。')
			print('连接正常。')

		if self.spider_info.max_Page == 0: # max_Page=0，此时获取当前关键词下的最大页数
			soup = BeautifulSoup(htmlContent, 'lxml')
			last_page_url = soup.find('link', title = 'Last Page')
			if last_page_url:
				self.spider_info.max_Page = int(soup.find('a', href = last_page_url['href']).string)
			else: # 只有一页
				self.spider_info.max_Page = 1

		self.urls = self.getPageUrls(self.spider_info)
		self.pic_infos = self.spider(self.urls, self.spider_info)
		self.pipelines(self.pic_infos)
		self.failed_pics = self.downloadPictures(self.pic_infos, self.spider_info)
		self.failed_pic_pipelines(self.failed_pics)

	
	def getPageUrls(self, spider_info):
		print('\n正在获取各个页面的URL...')
		urls = [] # 所有页面的URL
		pns = [str(i) for i in range(spider_info.start_Page, spider_info.max_Page + 1)]
		u1 = self.spider_info.start_URL.split('=')
		for pn in pns:
			u1[1] = pn + '&tags'
			url = '='.join(u1)
			urls.append(url)
		self.log.info('获取所有页面的URL成功')
		print('获取各个页面的URL成功。')
		return urls
	

	def spider(self, urls, spider_info): # 从搜索结果列表中获得每张符合要求图片的链接

		items = []
		counter = 1 # 记录解析页面数
		print('')
		for url in urls:
			# 解析批量下载链接所在JavaScript
			print('正在从页面中解析下载链接：%d / %d ...'%(counter, spider_info.max_Page - spider_info.start_Page + 1), end=' ')
			htmlContent = self.getResponseContent(url)
			if htmlContent == None:
				print('解析失败。')
			soup = BeautifulSoup(htmlContent, 'lxml')
			pic_tags = soup.find('script', attrs={'type':'text/javascript'}, text=re.compile(r"Post.register(\s\w+)?")).string.split('\n')
			
			# 用正则表达式解析下载链接所在的JavaScript
			for pic_tag in pic_tags[2:]:
				item = Yandere_Pic_Info()

				match_ID = re.findall(r'"id":.*?,', pic_tag) # 获取图片的yandere ID
				if match_ID:
					item.id = match_ID[0][5:-1]

				match_Tags = re.findall(r'"tags":".*?",', pic_tag) # 获取图片的所有标签
				if match_Tags:
					item.tags = match_Tags[0][8:-1]

				match_Score = re.findall(r'"score":.*?,', pic_tag) # 获取图片的评分
				if match_Score:
					item.score = int(match_Score[0][8:-1])

				match_Rating = re.findall(r'"rating":".*?"', pic_tag) # 获取图片的分级
				if match_Rating:
					if match_Rating[0][10] == 's':
						item.rating = 0
					elif match_Rating[0][10] == 'q':
						item.rating = 1
					elif match_Rating[0][10] == 'e':
						item.rating = 2

				match_URL = re.findall(r'"file_url":".*?"', pic_tag) # 获取图片的下载URL
				if match_URL:
					item.url = match_URL[0][12:-1]

				flag = True # 检查是否符合要求，符合要求则加入下载队列
				if item.score: # 检查该字符串是否为空
					if item.score < spider_info.min_Score:
						flag = False
					if not spider_info.rating[item.rating]:
						flag = False
					if spider_info.keyword_Num > 1:
						for kw in spider_info.extra_Keyword:
							if kw not in item.tags:
								flag = False
								break					
					if spider_info.filtered_Keyword_Num > 0:
						for kw in spider_info.filtered_Keyword:
							if kw in item.tags:
								flag = False
								break
					if flag:
						items.append(item)
			
			print('解析成功。')
			counter += 1
		return items
	

	def pipelines(self, items): # 将下载图片信息写入一个txt
		print('\n正在存储图片下载信息...')
		if not Path(self.spider_info.download_Path).exists():
			os.makedirs(self.spider_info.download_Path)
		path = str(self.spider_info.download_Path) + '图片下载信息.txt'
		with codecs.open(path, 'w', 'utf-8') as fp:
			for item in items:
				try:
					fp.write('ID: %s\r\nRating: %s\r\nURL: %s\r\n'%(item.id, item.rating, item.url))
				except Exception as e:
					print('存储失败。')
					self.log.error('写入文件失败')
				else:
					self.log.info('ID为<<%s>>的图片信息写入到"%s"成功'%(item.id, '图片下载信息.txt'))
		print('存储成功。')
	

	def downloadPictures(self, items, spider_info):
		failed_pics = []
		failed = 0

		# 定义下载线程
		class download_Thread(threading.Thread):
			def __init__(self, threadID, downloadNum, items, log):
				threading.Thread.__init__(self)
				self.threadID = threadID
				self.downloadNum = downloadNum
				self.items = items
				self.log = log
				self.running_status = True # 检查线程是否在进行中，不进行则加入新线程
				self.succeeded_download = True

			def run(self):
				# 为下载开始做准备
				print('开始下载第 %d / %d 张图片 (ID: %s)...'%(self.downloadNum + 1, len(items), items[self.downloadNum].id))
				self.log.info('开始下载第下载第%d/%d张图片(ID: %s)'%(self.downloadNum + 1, len(items), items[self.downloadNum].id))			
				pic_name = re.findall(r'yande.re%(.*)?', items[self.downloadNum].url)
				rating = ['safe', 'questionable', 'explicit']
				pic_name = 'yande.re_' + items[self.downloadNum].id + '_' + rating[items[self.downloadNum].rating] + '_' +  urllib.parse.unquote(pic_name[0]) # 处理下载图片名
				pic_name = pic_name.replace('/','').replace('"','').replace('\\','').replace(':','').replace('?','').replace('*','').replace('<','').replace('>','').replace('|','') # 去掉违法符号
				keywords = spider_info.keyword
				if spider_info.keyword_Num > 1:
					for kw in spider_info.extra_Keyword:
						keywords += ' ' + kw
				Path(spider_info.download_Path + keywords).mkdir(exist_ok=True)
				path = spider_info.download_Path + keywords + '\\' + pic_name

				# 下载过程
				try:
					times = 4
					while times > 0:
						file = requests.get(items[self.downloadNum].url)
						with open(path, 'wb') as f:
							try:
								f.write(file.content)
							except Exception as e:
								f.close() # 文件打印失败，再次尝试
								times -= 1
								time.sleep(1)
							else:
								f.close()
								if os.path.getsize(path) > 2**20: # 检查图片是否小于1MB，若小于1MB则再尝试下载三次
									break
								else:
									times -= 1
									time.sleep(1)
				except:
					print('下载第 %d / %d 张图片 (ID: %s) 失败。'%(self.downloadNum + 1, len(items), items[self.downloadNum].id))
					self.log.error('下载第%d/%d张图片(ID: %s)失败'%(self.downloadNum + 1, len(items), items[self.downloadNum].id))
					self.succeeded_download = False
				else:
					print('成功下载第 %d / %d 张图片 (ID: %s) 。'%(self.downloadNum + 1, len(items), items[self.downloadNum].id))
					self.log.info('成功下载第%d/%d张图片(ID: %s)'%(self.downloadNum + 1, len(items), items[self.downloadNum].id))

				# 子线程结束，状态切换到挂起
				self.running_status = False
		
		# 启动下载线程
		print()
		download_id = 0
		working_threads = []
		finished_threads = []
		while download_id < min(len(items), spider_info.thread_Num):
			thread = download_Thread(download_id, download_id, items, self.log)
			thread.start()
			working_threads.append(thread)
			download_id += 1
		while download_id < len(items):
			for t in working_threads:
				time.sleep(0.1)
				if not t.running_status:
					finished_threads.append(working_threads.pop(working_threads.index(t)))
					thread = download_Thread(t.threadID, download_id, items, self.log)
					thread.start()
					working_threads.append(thread)
					download_id += 1		
					if download_id >= len(items):
						break
		for t in finished_threads:
			t.join()
			if not t.succeeded_download:
				failed_pics.append(items[t.downloadNum]) # 下载失败，存入文档
		return failed_pics

	def failed_pic_pipelines(self, failed_pics): # 存储下载失败图片信息		
		if failed_pics:
			print('\n正在存储下载失败图片信息...')
			path = str(self.spider_info.download_Path) + '下载失败图片信息.txt'
			with codecs.open(path, 'w', 'utf-8') as fp:
				for item in failed_pics:
					try:
						fp.write('ID: %s\r\nRating: %s\r\nURL: %s\r\n'%(item.id, item.rating, item.url))
					except Exception as e:
						print('存储失败。')
						self.log.error('写入文件失败')
					else:
						self.log.info('ID为<<%s>>的图片信息写入到"%s"成功'%(item.id, '下载失败图片信息.txt'))
			print('存储成功。')

		print('共计%s 个图片下载成功，%s 个图片下载失败。'%(str(len(self.pic_infos) - len(failed_pics)), str(len(failed_pics))))


	def getResponseContent(self, url): # 分析URL并取得HTML内容
		random.seed()
		if self.spider_info.delay_Time >= 0: # 爬取间隔
			time.sleep(self.spider_info.delay_Time)
		else:
			time.sleep(random.random()*(-self.spider_info.delay_Time))
		
		# 访问头伪装
		headers_browser_dic = UserAgent().pcUserAgent
		# proxy_dic = {'http':'http://127.0.0.1:8080'}
		# proxy_handler = urllib.request.ProxyHandler(proxy_dic)
		# opener = urllib.request.build_opener(proxy_handler)
		# urllib.request.install_opener(opener)
		headers = {'User-Agent': random.choice(list(headers_browser_dic.values()))}

		urlList = url.split('=')
		try:
			req = urllib.request.Request(url,headers = headers)
			response = urllib.request.urlopen(req)
		except:
			self.log.error('Python返回URL: %s 数据失败'%url)
		else:
			self.log.info('Python返回URL: %s 数据成功'%url)
			return response.read()

def startup_Prompts(): # 程序抬头提示
	print('yande.re Spider')
	print('制作: Akiha Tatsu in USTC\t2021/4/23')
	print('Ver: 1.1.0\n')
	print('提醒：')
	print('（1）请务必按照格式输入！')
	print('（2）请不要填写过短的爬取间隔，或过高的线程数！\n')


if __name__ == '__main__':
	startup_Prompts()
	Requirements = Download_Requirements()
	Requirements.Get_Requirements()
	print(Requirements.Output_Info())
	Spider = Yandere_InfoLink_Download(Requirements)
	input('按回车键结束...') # 程序结束后暂停
