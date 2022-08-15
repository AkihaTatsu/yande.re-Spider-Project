import threading

import urllib.request
import urllib.parse
from UserAgent import UserAgent
import requests

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
            html_content = get_response_content(
                url=self.url, 
                delay_time=self.args.delay_time, 
                if_randomize_time=self.args.if_randomize_time, 
                log=self.log,
                proxy=None if (self.args.proxy_type == '' or self.args.proxy == '') else {self.args.proxy_type: self.args.proxy}
            )
            if html_content is None:
                times -= 1
                self.log.warning('Retrying URL (%d times left): %s'%(times, self.url))
                time.sleep(30)  # 重试间隔60s
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


# 生成图片存储路径
def generate_pic_path_name(item, args):
    pic_name = re.findall(r'yande.re%(.*)?', item.url)
    rating = ['safe', 'questionable', 'explicit']
    pic_name = 'yande.re_' + item.id + '_' + rating[item.rating] + '_' +  urllib.parse.unquote(pic_name[0]) # 处理下载图片名
    pic_name = pic_name.replace('/','').replace('"','').replace('\\','').replace(':','').replace('?','').replace('*','').replace('<','').replace('>','').replace('|','')  # 去掉违法符号
    keywords = ' '.join(args.keywords)
    Path(os.path.join(args.path, keywords)).mkdir(exist_ok=True)

    return os.path.join(args.path, keywords, ''), pic_name



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
        self.log.info('Downloading picture ID: %s from URL: %s'%(self.item.id, self.item.url))
        
        folder_path, pic_name = generate_pic_path_name(self.item, self.args)
        path = os.path.join(folder_path, pic_name)

        # 下载过程
        try:
            times = 4
            while times > 0:
                if self.args.if_randomize_time:  # 需要随机化爬取间隔
                    time.sleep(random.random()*self.args.delay_time)
                else:
                    time.sleep(self.args.delay_time)
                    
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
                    except Exception as e:  # 文件存储到本地失败，再次尝试
                        self.log.warning(f'Error {e}, retrying download picture {self.item.id} ({times} times left): %s')
                        f.close()
                        times -= 1
                        time.sleep(60)  # 重试间隔60s
                    else:
                        f.close()

                        # 检查MD5是否一致，一致则结束
                        with open(path, 'rb') as fp:
                            full_data = fp.read()
                        file_md5 = hashlib.md5(full_data).hexdigest()
                        if file_md5 == self.item.md5:
                            break
                        else:
                            self.log.warning(f'File damaged, retrying download picture {self.item.id} ({times} times left): %s')
                            times -= 1
                            time.sleep(60)  # 重试间隔60s

            if times <= 0:  # 所有下载尝试失败
                self.log.error(f'All retrial failed, Downloading picture ID: {self.item.id} failed from URL: {self.item.url}')
                self.succeeded_download = False
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