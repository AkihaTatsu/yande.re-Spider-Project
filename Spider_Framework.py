import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

import re

import time
import datetime
from tqdm import tqdm
from Log import Log

from Download_Thread import Download_Thread_HTML, Download_Thread_Pics, get_response_content
from Config import Spider_Config



# 图片信息
class Yandere_Pic_Info():
    def __init__(self):
        self.url = None
        self.id = None
        self.tags = None
        self.score = None
        self.rating = None  # 0为safe，1为questionable，2为explicit
        self.height = None
        self.width = None
        self.author = None
        self.source = None
        self.md5 = None
        self.is_downloaded = False


# 爬虫基本框架
class Yandere_Spider_Framework():
    def __init__(self, args):
        self.args = args
        self.begin_time = datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S ')
        self.log = Log(self.args.path, self.begin_time, self.args.keywords)
        self.start_URL = 'https://yande.re/post?page=' + str(self.args.start_page) + '&tags=' + urllib.parse.quote(self.args.keywords[0])
        self.spider_type = 'Basic'

        self.page_urls = None  # 所有索引页URL，类型为字符串的列表
        self.page_html_contents = None  # 所有索引页HTML内容，格式为{'num': int, 'content': HTML}，num参数指明对应page_url索引
        self.pic_infos = None  # 所有图片信息，类型为Yandere_Spider_Info或衍生类型的列表
        self.filtered_pic_infos = None  # 所有过滤后的图片信息，类型为Yandere_Spider_Info或衍生类型的列表

        # 保存至Config
        self.config = Spider_Config(args=self.args, begin_time=self.begin_time, spider_type=self.spider_type)
        self.config.write_config()
        

    # 连接测试
    def connection_test(self):
        self.log.info('Testing connectivity...')
        print('Testing connectivity...')

        # 先进行一次访问，测试能否连接        
        html_content = get_response_content(
            url='https://yande.re/', 
            delay_time=self.args.delay_time, 
            if_randomize_time=self.args.if_randomize_time, 
            log=self.log,
            proxy=None if (self.args.proxy_type == '' or self.args.proxy == '') else {self.args.proxy_type: self.args.proxy}
        )
        
        if html_content is None:
            self.log.critical('Failed to connect.')
            print('Failed to connect. Check your connection or proxy first.')
            return False
        else:
            self.log.info('Successfully connected.')
            print('Successfully connected.')
            return True


    # 生成页面连接
    def get_page_urls(self):
        # 连接至第一页
        self.log.info('Connect to the first page...')
        print('Connect to the first page...')
        
        html_content = get_response_content(
            url=self.start_URL, 
            delay_time=self.args.delay_time, 
            if_randomize_time=self.args.if_randomize_time, 
            log=self.log,
            proxy=None if (self.args.proxy_type == '' or self.args.proxy == '') else {self.args.proxy_type: self.args.proxy}
        )
            
        if html_content is None:
            self.log.critical('Failed to connect.')
            print('Failed to connect. Check your connection or proxy first.')
            exit(0)

        # finish_page = -1，此时获取当前关键词下的最大页数
        if self.args.finish_page == -1:
            soup = BeautifulSoup(html_content, 'lxml')
            last_page_url = soup.find('link', title = 'Last Page')
            if last_page_url:
                self.args.finish_page = int(soup.find('a', href = last_page_url['href']).string)
            else:  # 只有一页
                self.args.finish_page = 1

        # 获得所有页面的url
        self.log.info('Parsing all page urls...')
        print('Parsing all page urls...')
        page_urls = []  # 所有页面的URL
        pns = [str(i) for i in range(self.args.start_page, self.args.finish_page + 1)]
        u1 = self.start_URL.split('=')
        for pn in pns:
            u1[1] = pn + '&tags'
            url = '='.join(u1)
            page_urls.append(url)
        self.log.info('Successfully parsed all page urls.')
        print('Successfully parsed all page urls.')
        
        # 保存所有索引页面URL至Config
        self.config = Spider_Config(args=self.args, begin_time=self.begin_time, spider_type=self.spider_type, page_urls=page_urls)
        self.config.write_config()

        self.page_urls = page_urls
        return page_urls


    # 获取所有图片索引页面HTML
    def get_page_html(self, page_urls):
        page_html_contents = []
        
        # 下载每一页的HTML内容
        self.log.info('Downloading HTML contents from index pages...')
        print('Downloading HTML contents from index pages...')
        with tqdm(total=len(page_urls), desc="Downloaded Pages", ascii=True) as pbar:            
            download_id = 0
            working_threads = []
            finished_threads = []

            # 启动所有可用线程
            while download_id < min(len(page_urls), self.args.thread_num):
                thread = Download_Thread_HTML(
                    self.page_urls[download_id], args=self.args, log=self.log,
                    threadID=download_id,
                )
                thread.start()
                working_threads.append(thread)
                download_id += 1

            # 当某一线程结束后开始下一线程
            while len(working_threads) > 0:  # 只有进行中线程全部结束后再进入下一步
                for t in working_threads:
                    time.sleep(0.01)  # 线程状态检测间隔0.01s
                    if not t.running_status:
                        pbar.update(1)
                        finished_threads.append(working_threads.pop(working_threads.index(t)))

                        if not t.succeeded_download:  # 有页面未能成功下载，程序直接结束！
                            self.log.critical(f"Page {t.url} download failed! Program exited.")
                            print(f"Page {t.url} download failed! Program exited.")
                            exit(0)

                        if download_id < len(page_urls):
                            thread = Download_Thread_HTML(
                                self.page_urls[download_id], args=self.args, log=self.log, 
                                threadID=download_id
                            )
                            thread.start()
                            working_threads.append(thread)
                            download_id += 1
                        else:
                            break

            for t in finished_threads:
                page_html_contents.append({'num': t.threadID, 'content': t.join()})
        
        self.page_html_contents = page_html_contents
        self.log.info('Downloading HTML contents from index pages succeeded.')
        print('Downloading HTML contents from index pages succeeded.')
        return page_html_contents


    # 解析图片URL和标签
    def parse_pic_infos(self, html_contents_list):
        pic_infos = []

        self.log.info('Parsing picture info...')
        print('Parsing picture info...')

        for html_content in html_contents_list:
            soup = BeautifulSoup(html_content['content'], 'lxml')
            pic_tags = soup.find('script', attrs={'type': 'text/javascript'}, text=re.compile(r"Post.register(\s\w+)?")).string.split('\n')

            # 用正则表达式解析下载链接所在的JavaScript
            for pic_tag in pic_tags[2:]:
                item = Yandere_Pic_Info()

                match_URL = re.findall(r'"file_url":".*?"', pic_tag)  # 获取图片的下载URL
                if match_URL:
                    item.url = match_URL[0][12:-1]

                match_ID = re.findall(r'"id":.*?,', pic_tag)  # 获取图片的yandere ID
                if match_ID:
                    item.id = match_ID[0][5:-1]

                match_tags = re.findall(r'"tags":".*?",', pic_tag)  # 获取图片的所有标签
                if match_tags:
                    item.tags = match_tags[0][8:-1]

                match_score = re.findall(r'"score":.*?,', pic_tag)  # 获取图片的评分
                if match_score:
                    item.score = int(match_score[0][8:-1])

                match_rating = re.findall(r'"rating":".*?"', pic_tag)  # 获取图片的分级
                if match_rating:
                    if match_rating[0][10] == 's':
                        item.rating = 0
                    elif match_rating[0][10] == 'q':
                        item.rating = 1
                    elif match_rating[0][10] == 'e':
                        item.rating = 2
                
                match_width = re.findall(r'"width":.*?,', pic_tag)  # 获取图片的宽度
                if match_width:
                    item.width = int(match_width[0][8:-1])

                match_height = re.findall(r'"height":.*?,', pic_tag)  # 获取图片的高度
                if match_height:
                    item.height = int(match_height[0][9:-1])                    
                    
                match_author = re.findall(r'"author":".*?"', pic_tag)  # 获取图片的作者
                if match_author:
                    item.author = match_author[0][10:-1]

                match_source = re.findall(r'"source":".*?"', pic_tag)  # 获取图片的来源
                if match_source:
                    item.source = match_source[0][10:-1]

                match_md5 = re.findall(r'"md5":".*?"', pic_tag)  # 获取图片的来源
                if match_md5:
                    item.md5 = match_md5[0][7:-1]

                if item.id is not None:  # 跳过不合法内容
                    pic_infos.append(item)

        
        self.log.info('Parsing picture info finished.')
        print('Parsing picture info finished.')

        self.pic_infos = pic_infos
        return pic_infos


    # 根据要求进行筛选
    def filter_pic_infos(self, pic_infos):

        # 保存未筛选图片信息至Config
        self.config = Spider_Config(args=self.args, begin_time=self.begin_time, spider_type=self.spider_type, pic_infos=pic_infos)
        self.config.write_config()

        filtered_pic_infos = []
        for item in pic_infos:
            flag = True  # flag=True表示符合条件

            # 评分低于最低分
            if item.score < self.args.min_score:
                flag = False
                
            # 评级不符合
            if item.rating == 0 and self.args.if_no_safe:
                flag = False
            if item.rating == 1 and self.args.if_no_questionable:
                flag = False
            if item.rating == 2 and self.args.if_no_explicit:
                flag = False

            # 存在多个关键词，检查是否全部在tags中
            for kw in self.args.keywords:
                if kw not in item.tags:
                    flag = False
                    break
            
            # 存在需要过滤的关键词，检查是否在tags中存在
            for kw in self.args.filtered_keywords:
                if kw in item.tags:
                    flag = False
                    break

            if flag:
                filtered_pic_infos.append(item)

        self.filtered_pic_infos = filtered_pic_infos
        return filtered_pic_infos


    # 下载图片
    def download_pics(self, pic_infos):
        new_pic_infos = pic_infos

        # 保存筛选后图片信息至Config（开始下载前）
        self.config = Spider_Config(
            args=self.args, begin_time=self.begin_time, spider_type=self.spider_type, 
            filtered_pic_infos=new_pic_infos
        )
        self.config.write_config()

        # 只下载还未下载的图片
        undownloaded_pic_indexes = []
        for i in range(len(new_pic_infos)):
            if new_pic_infos[i].is_downloaded is False:
                undownloaded_pic_indexes.append(i)

        success_num = 0

        self.log.info('Downloading pictures...')
        print('Downloading pictures...')
        with tqdm(total=len(undownloaded_pic_indexes), desc="Downloaded Pictures", ascii=True) as pbar:
            download_id = 0
            working_threads = []
            finished_threads = []

            # 启动所有可用线程
            while download_id < min(len(undownloaded_pic_indexes), self.args.thread_num):
                thread = Download_Thread_Pics(
                    new_pic_infos[undownloaded_pic_indexes[download_id]], args=self.args, log=self.log,
                    threadID=download_id,
                )
                thread.start()
                working_threads.append(thread)
                download_id += 1

            # 当某一线程结束后开始下一线程
            while len(working_threads) > 0:  # 只有进行中线程全部结束后再进入下一步

                # 当下载数达到线程数的倍数时，保存一次下载状况
                if download_id % self.args.thread_num == 0:
                    self.config = Spider_Config(
                        args=self.args, begin_time=self.begin_time, spider_type=self.spider_type, 
                        filtered_pic_infos=new_pic_infos
                    )
                    self.config.write_config()

                for t in working_threads:
                    time.sleep(0.01)  # 线程状态检测间隔0.01s
                    if not t.running_status:
                        pbar.update(1)
                        finished_threads.append(working_threads.pop(working_threads.index(t)))

                        if t.succeeded_download:
                            new_pic_infos[undownloaded_pic_indexes[t.threadID]].is_downloaded = True
                        else:
                            tqdm.write(f'Downloading Picture {t.item.id} failed.')
                            
                        if download_id < len(undownloaded_pic_indexes):
                            thread = Download_Thread_Pics(
                                new_pic_infos[undownloaded_pic_indexes[download_id]], args=self.args, log=self.log,
                                threadID=download_id,
                            )
                            thread.start()
                            working_threads.append(thread)
                            download_id += 1
                        else:
                            break

            for t in finished_threads:
                if t.join():
                    success_num += 1
                
        # 下载结束，保存一次config
        self.config = Spider_Config(
            args=self.args, begin_time=self.begin_time, spider_type=self.spider_type, 
            filtered_pic_infos=new_pic_infos
        )
        self.config.write_config()

        self.log.info('Downloading pictures finished. %d succeeded, %d failed.'%(success_num, len(undownloaded_pic_indexes) - success_num))
        print('Downloading pictures finished. %d succeeded, %d failed.'%(success_num, len(undownloaded_pic_indexes) - success_num))

        # 更新下载图片信息
        self.filtered_pic_infos
        return new_pic_infos
        

