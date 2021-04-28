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


class Saved_Text_Pic_Info(object):
	id = None
	rating = None
	url = None


class Saved_Text_Download_Requirements(object):
	def __init__(self):
		self.file_Name = None		# 存储文件名
		self.delay_Time = -10		# 爬虫间隔
		self.thread_Num = 5			# 线程数量
		self.download_Path = None	# 存储路径

	def Get_Requirements(self):	
		test_Character = str(input('是否使用文件中已有预设？(Y/N): '))
		if test_Character == 'Y' or test_Character == 'y': # 使用文件中预设
			file_Name_0 = str(input('请输入预设文件名: '))
			file = open(file_Name_0, 'r')
			file_Content = file.read().split('\n')
			self.file_Name = file_Content[0]
			self.download_Path = file_Content[1]
			self.delay_Time = int(file_Content[2])
			self.thread_Num = int(file_Content[3])
		else:
			# 获得文件名
			self.file_Name = str(input('请输入文件名: '))
			# 获得存储路径
			self.download_Path = str(input('请输入存储路径 <不能为空！>: '))
			# 获得爬虫间隔
			test_Character = str(input('请输入爬取时间间隔（单位：s）（默认为-10，-n代表在0到n间产生一个随机数）: ')) # 用于检测输入是否为空
			if test_Character != '':
				self.delay_Time = int(test_Character)
			# 获得线程数量
			test_Character = str(input('请输入线程数量（默认为5）: ')) # 用于检测输入是否为空
			if test_Character != '':
				self.thread_Num = int(test_Character)

	def Output_Info(self): # 返回当前爬取要求信息的字符串，可用于写入日志或检查
		output_Str = '\r\n文件名: ' + str(self.file_Name)\
				   + '\r\n爬取时间间隔: ' + str(self.delay_Time)\
				   + '\r\n线程数量: ' + str(self.thread_Num)\
				   + '\r\n存储路径: ' + str(self.download_Path)
		return output_Str


# 用于从已保存的文本中下载
class Saved_Text_Download(object):
	
	def __init__(self, download_requirements):
		self.download_requirements = download_requirements		
		self.log = mylog()
		
		self.pic_infos = self.readText(self.download_requirements.file_Name)
				
		htmlContent = self.getResponseContent(r'https://yande.re/post') # 先进行一次访问，测试能否连接
		if htmlContent == None:
			self.log.critical('连接: yande.re 失败。程序结束。')
			print('yande.re访问失败。请检查网络连接。')
			return
		else:
			self.log.info('连接: yande.re 成功。')
			print('连接正常。')

		if self.pic_infos:
			self.failed_pics = self.downloadPictures(self.pic_infos, download_requirements)
			self.failed_pic_pipelines(self.failed_pics)

	def readText(self, file_Name): # 读取文本
		try:
			print('正在读取文本...')
			file = open(file_Name, 'r')
		except:
			print('读取失败。')
			self.log.critical('%s 打开失败'%file_Name)
			return None
		else:
			print('读取成功。')
			self.log.info('%s 打开成功'%file_Name)
			
			file_Content = file.read().split('\n')
			items = []
			count = 0

			for i in range(0, len(file_Content[:-1]) // 3):
				item = Saved_Text_Pic_Info()
				item.id = file_Content[i * 3][4:]
				item.rating = int(file_Content[i * 3 + 1][8])
				item.url = file_Content[i * 3 + 2][5:]
				items.append(item)

			return items


	def downloadPictures(self, items, download_info):		
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
				
				if not Path(download_info.download_Path).exists():
					os.makedirs(download_info.download_Path)
				path = download_info.download_Path + '\\' + pic_name
				
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
		while download_id < min(len(items), download_info.thread_Num):
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
			path = str(self.download_requirements.download_Path) + '下载失败图片信息_文本.txt'
			with codecs.open(path, 'w', 'utf-8') as fp:
				for item in failed_pics:
					try:
						fp.write('ID: %s\r\nRating: %s\r\nURL: %s\r\n'%(item.id, item.rating, item.url))
					except Exception as e:
						print('存储失败。')
						self.log.error('写入文件失败')
					else:
						self.log.info('ID为<<%s>>的图片信息写入到"%s"成功'%(item.id, '下载失败图片信息_文本.txt'))
			print('存储成功。')

		print('共计%s 个图片下载成功，%s 个图片下载失败。'%(str(len(self.pic_infos) - len(failed_pics)), str(len(failed_pics))))

	
	def getResponseContent(self, url): # 分析URL并取得HTML内容
		random.seed()
		if self.download_requirements.delay_Time >= 0: # 爬取间隔
			time.sleep(self.download_requirements.delay_Time)
		else:
			time.sleep(random.random()*(-self.download_requirements.delay_Time))
		
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


def startup_Prompts_Saved_Text(): # 程序抬头提示
	print('本程序处理相应的文本文档内URL下载。')
	print('Ver: 1.0.0 \r\n')


if __name__ == '__main__':
	startup_Prompts_Saved_Text()
	Requirements = Saved_Text_Download_Requirements()
	Requirements.Get_Requirements()
	print(Requirements.Output_Info())
	Spider = Saved_Text_Download(Requirements)
	input('按回车键结束...') # 程序结束后暂停
