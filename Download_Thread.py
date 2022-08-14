import threading

import urllib.request
import urllib.parse
from UserAgent import UserAgent
import requests
from bs4 import BeautifulSoup

import time
import random
import re
import os
from pathlib import Path
from tqdm import tqdm
import hashlib



# 分析URL并取得HTML内容
def get_response_content(url, delay_time, if_randomize_time, log, proxy=None):
    random.seed()
    if if_randomize_time:  # 需要随机化爬取间隔
        time.sleep(random.random()*delay_time)
    else:
        time.sleep(delay_time)
    
    # 访问头伪装
    headers_browser_dic = UserAgent.pcUserAgent

    # 代理设置
    if proxy is not None:
        proxy_handler = urllib.request.ProxyHandler(proxy)
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
    headers = {'User-Agent': random.choice(list(headers_browser_dic.values()))}

    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
    except:
        log.error('Parsing URL data failed: %s'%url)
    else:
        log.info('Parsing URL data succeeded: %s'%url)
        return response.read()


# HTML批量下载线程
class Download_Thread_HTML(threading.Thread):
    def __init__(self, url, args, log, threadID):
        super().__init__()
        self.url = url
        self.args = args
        self.log = log

        self.threadID = threadID
        self.running_status = True # 检查线程是否在进行中，不进行则加入新线程
        self.succeeded_download = True


    def run(self):
        self.log.info('Downloading html from URL: %s'%self.url)
        
        times = 4
        while times > 0:
            if self.args.proxy_type == '' or self.args.proxy == '':
                html_content = get_response_content(
                    url=self.url, 
                    delay_time=self.args.delay_time, 
                    if_randomize_time=self.args.if_randomize_time, 
                    log=self.log,
                )
            else:
                html_content = get_response_content(
                    url=self.url, 
                    delay_time=self.args.delay_time, 
                    if_randomize_time=self.args.if_randomize_time, 
                    log=self.log,
                    proxy={self.args.proxy_type: self.args.proxy}
                )
            if html_content is None:
                self.log.info('Retrying URL (%d times left): %s'%(times, self.url))
                times -= 1
                time.sleep(1)
            else:
                break

        if html_content is None:
            self.log.error('Downloading html from URL: %s failed.'%self.url)
            self.succeeded_download = False
            self._return = None
        else:
            self.log.info('Downloading html from URL: %s succeeded.'%self.url)

        self._return = html_content

        # 子线程结束，状态切换到挂起
        self.running_status = False


    def join(self):
        super().join()
        return self._return


# 图片批量下载线程
class Download_Thread_Pics(threading.Thread):
    def __init__(self, item, args, log, threadID):
        super().__init__()
        self.item = item
        self.args = args
        self.log = log

        self.threadID = threadID
        self.running_status = True # 检查线程是否在进行中，不进行则加入新线程
        self.succeeded_download = True


    def run(self):
        self.log.info('Downloading picture from URL: %s'%self.item.url)
        
        pic_name = re.findall(r'yande.re%(.*)?', self.item.url)
        rating = ['safe', 'questionable', 'explicit']
        pic_name = 'yande.re_' + self.item.id + '_' + rating[self.item.rating] + '_' +  urllib.parse.unquote(pic_name[0]) # 处理下载图片名
        pic_name = pic_name.replace('/','').replace('"','').replace('\\','').replace(':','').replace('?','').replace('*','').replace('<','').replace('>','').replace('|','')  # 去掉违法符号
        keywords = ' '.join(self.args.keywords)
        Path(os.path.join(self.args.path, keywords)).mkdir(exist_ok=True)
        path = os.path.join(self.args.path, keywords) + '\\' + pic_name

        # 下载过程
        try:
            times = 4
            while times > 0:
                if self.args.proxy_type == '' or self.args.proxy == '':
                    file = requests.get(self.item.url, stream=True)
                else:
                    file = requests.get(self.item.url, proxies={self.args.proxy_type: self.args.proxy}, stream=True)
                file_size = int(file.headers.get('content-length', 0))
                with open(path, 'wb') as f:
                    try:
                        with tqdm(
                            desc=f'Thread {self.threadID}, Pic {self.item.id}',
                            total=file_size,
                            unit='iB',
                            unit_scale=True,
                            unit_divisor=1024,
                            ascii=True,
                            leave=False,
                        ) as pbar:
                            for data in file.iter_content(chunk_size=1024):
                                size = f.write(data)
                                pbar.update(size)
                    except Exception as e:
                        f.close() #  文件打印失败，再次尝试
                        times -= 1
                        time.sleep(1)
                    else:
                        f.close()
                        if os.path.getsize(path) > 2**20:  # 检查图片是否小于1MB，若小于1MB则再尝试下载三次
                            break
                        else:
                            times -= 1
                            time.sleep(1)
        except Exception as e:
            self.log.error(f'Error {e}, Downloading picture ID: {self.item.id} failed from URL: {self.item.url}')
            self.succeeded_download = False
        else:
            self.log.info('Downloading picture ID: %s succeeded from URL: %s'%(self.item.id, self.item.url))

        # 子线程结束，状态切换到挂起
        self.running_status = False


    def join(self):
        super().join()
        return self.succeeded_download