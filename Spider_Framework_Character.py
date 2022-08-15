import re
import time
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path
import shutil
import os

from Spider_Framework import Yandere_Spider_Framework, Yandere_Pic_Info
from Download_Thread import Download_Thread_HTML, generate_pic_path_name



# 图片信息（分角色）
class Yandere_Pic_Info_Char(Yandere_Pic_Info):
    def __init__(self):
        super().__init__()
        self.char_tags = None  # 图片所属角色标签

    def copy_from_yandere_pic_info(self, pic_info):
        for arg in vars(pic_info):
            vars(self)[arg] = vars(pic_info)[arg]



# 角色分类爬虫基本框架
class Yandere_Spider_Framework_Character(Yandere_Spider_Framework):
    def __init__(self, args):
        super().__init__(args)
        self.spider_type = 'Classify by characters'


    # 获得图片的角色标签，返回新图片信息类型
    def get_pic_char_tags(self, pic_infos):

        # 将原图片信息类型转换为当前类型
        new_pic_infos = []
        for pic_info in pic_infos:
            new_pic_info = Yandere_Pic_Info_Char()
            new_pic_info.copy_from_yandere_pic_info(pic_info)
            new_pic_infos.append(new_pic_info)

        pic_preview_html_contents = []
        
        # 下载每一页的HTML内容
        self.log.info('Downloading HTML contents from picture preview pages...')
        print('Downloading HTML contents from picture preview pages...')
        with tqdm(total=len(new_pic_infos), desc="Downloaded Pages", ascii=True) as pbar:            
            download_id = 0
            working_threads = []
            finished_threads = []

            # 启动所有可用线程
            while download_id < min(len(new_pic_infos), self.args.thread_num):
                thread = Download_Thread_HTML(
                    url='https://yande.re/post/show/' + new_pic_infos[download_id].id,
                    args=self.args, log=self.log,
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
                        if download_id < len(new_pic_infos):
                            thread = Download_Thread_HTML(
                                url='https://yande.re/post/show/' + new_pic_infos[download_id].id,
                                args=self.args, log=self.log,
                                threadID=download_id,
                            )
                            thread.start()
                            working_threads.append(thread)
                            download_id += 1
                        else:
                            break

            for t in finished_threads:
                pic_preview_html_contents.append({'num': t.threadID, 'content': t.join()})  # 包含原图的序号和对应预览页的HTML内容
        
        self.log.info('Downloading HTML contents from picture preview pages succeeded.')
        print('Downloading HTML contents from picture preview pages succeeded.')
        
        
        self.log.info('Parsing character tags...')
        print('Parsing character tags...')
        for preview_html_content in pic_preview_html_contents:
            # 获得当前图片内所有角色标签
            match_char_tags = []
            soup = BeautifulSoup(preview_html_content['content'], 'lxml')
            res = soup.find_all('li', class_="tag-type-character")
            for chara in res:
                match_char_tags.append(chara.find_all('a')[1].string.replace('/','').replace('"','').replace('\\','').replace(':','').replace('?','').replace('*','').replace('<','').replace('>','').replace('|',''))  # 替换非法字符
            if len(match_char_tags) > 0:
                new_pic_infos[preview_html_content['num']].char_tags = match_char_tags
        self.log.info('Parsing character tags finished.')
        print('Parsing character tags finished.')

        return new_pic_infos


    # 移动所有图片
    def move_all_pictures(self, pic_infos):
        self.log.info('Moving pictures to character folders...')
        print('Moving pictures to character folders...')
        for info in pic_infos:
            if info.char_tags is not None:
                self.move_pictures(info)  # 增加移动图片步骤
        self.log.info('Moving pictures to character folders finished.')
        print('Moving pictures to character folders finished.')


    # 移动图片至所属角色文件夹
    def move_pictures(self, item):
        folder_path, pic_name = generate_pic_path_name(item, self.args)
        success_move = True
        for chara in item.char_tags:
            try:
                Path(os.path.join(folder_path, chara)).mkdir(exist_ok=True)
                path = os.path.join(folder_path, pic_name)
                path_2 = os.path.join(folder_path, chara) + '\\' + pic_name
                shutil.copyfile(path, path_2)
                self.log.info(f'Moving picture (ID: {item.id}) to folder {chara} succeeded.')
            except Exception as e:
                self.log.error(f'Error {e}, moving picture (ID: {item.id}) to folder {chara} failed.')
                print(f'moving picture (ID: {item.id}) to folder {chara} failed.')
                success_move = False

        if success_move:
            os.remove(path)

        return success_move
        

