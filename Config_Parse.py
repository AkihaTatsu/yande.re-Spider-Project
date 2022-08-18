import os
import json
import argparse

from Config import Spider_Config
from Spider_Framework import Yandere_Spider_Framework, Yandere_Pic_Info
from Spider_Framework_Character import Yandere_Spider_Framework_Character, Yandere_Pic_Info_Char
from Command_Utils import display_info



# 解析json中的config并继续下载的模块
class Spider_Config_Parse(Spider_Config):
    def __init__(
        self, args, 
        page_urls=None, 
        page_html_contents=None, 
        pic_infos=None, 
        filtered_pic_infos=None,
    ):
        super().__init__(args, page_urls, page_html_contents, pic_infos, filtered_pic_infos)

    
    # 读取Json进度文件并解析
    def read_config(self, json_name):
        with open(json_name, 'r+', encoding='utf8') as f:
            self.json_str = f.read()

        parsed_str = json.loads(self.json_str)
        self.spider_type = parsed_str['spider_type']
        self.state = parsed_str['state']
        self.args = self.dict_to_args(parsed_str['args'])

        if self.spider_type == 'Basic':
            if self.state == 1:
                self.page_urls = parsed_str['page_urls']
            elif self.state == 2:
                self.pic_infos = []
                for pic_info in parsed_str['pic_infos']:
                    self.pic_infos.append(self.dict_to_class(pic_info, Yandere_Pic_Info))
            elif self.state == 3:
                self.filtered_pic_infos = []
                for filtered_pic_info in parsed_str['filtered_pic_infos']:
                    self.filtered_pic_infos.append(self.dict_to_class(filtered_pic_info, Yandere_Pic_Info))
        elif self.spider_type == 'Classify by characters':
            if self.state == 1:
                self.page_urls = parsed_str['page_urls']
            elif self.state == 2:
                self.pic_infos = []
                for pic_info in parsed_str['pic_infos']:
                    self.pic_infos.append(self.dict_to_class(pic_info, Yandere_Pic_Info))
            elif self.state == 3:
                self.filtered_pic_infos = []
                for filtered_pic_info in parsed_str['filtered_pic_infos']:
                    self.filtered_pic_infos.append(self.dict_to_class(filtered_pic_info, Yandere_Pic_Info_Char))


    # 根据当前进度继续下载
    def continue_download(self):
        display_info(self.args)

        if self.spider_type == 'Basic':
            spider = Yandere_Spider_Framework(self.args)
            if self.state <= 0:
                # spider.connection_test()
                spider.get_page_urls()
            else:
                pass

            if self.state <= 1:
                if self.state == 1:
                    spider.page_urls = self.page_urls
                spider.get_page_html(spider.page_urls)
                spider.parse_pic_infos(spider.page_html_contents)
            else:
                pass

            if self.state <= 2:
                if self.state == 2:
                    spider.pic_infos = self.pic_infos
                spider.filter_pic_infos(spider.pic_infos)
            else:
                pass

            if self.state <= 3:
                if self.state == 3:
                    spider.filtered_pic_infos = self.filtered_pic_infos
                spider.download_pics(spider.filtered_pic_infos)
            else:
                pass
            
        elif self.spider_type == 'Classify by characters':
            spider = Yandere_Spider_Framework_Character(self.args)
            if self.state <= 0:
                # spider.connection_test()
                spider.get_page_urls()
            else:
                pass

            if self.state <= 1:
                if self.state == 1:
                    spider.page_urls = self.page_urls
                spider.get_page_html(spider.page_urls)
                spider.parse_pic_infos(spider.page_html_contents)
            else:
                pass

            if self.state <= 2:
                if self.state == 2:
                    spider.pic_infos = self.pic_infos
                spider.filter_pic_infos(spider.pic_infos)
                spider.filtered_pic_infos = spider.get_pic_char_tags(spider.filtered_pic_infos)
            else:
                pass

            if self.state <= 3:
                if self.state == 3:
                    spider.filtered_pic_infos = self.filtered_pic_infos
                spider.download_pics(spider.filtered_pic_infos)
                spider.move_all_pictures(spider.filtered_pic_infos)
            else:
                pass



# 继续下载
def parse_args_config():
    parser = argparse.ArgumentParser(description="# ================== Help ================== #")

    parser.add_argument('--json-path', type=str, default='', help="Json path")

    return parser.parse_args()


if __name__ == '__main__':
    config_args = parse_args_config()
    config = Spider_Config_Parse(args=None)
    if len(config_args.json_path.strip()) > 0:
        json_name = config_args.json_path.strip()
    else:
        json_name = input('Please input json file name:')
        while len(json_name.strip()) == 0:
            json_name = input('Invalid input. Please input json file name:')
    config.read_config(json_name)
    config.continue_download()