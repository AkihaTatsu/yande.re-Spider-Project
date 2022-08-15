import json
import os
import datetime

from Command_Utils import parse_args
from Log import Log



class Spider_Config():
    def __init__(
        self,
        args,
        spider_type='Basic',
        begin_time=None,
        page_urls=None,
        pic_infos=None,
        filtered_pic_infos=None,
    ):
        self.args = args
        self.spider_type = spider_type  # 使用的爬虫类型
        self.begin_time = begin_time
        self.page_urls = page_urls
        self.pic_infos = pic_infos
        self.filtered_pic_infos = filtered_pic_infos
        self.json_str = None
        
        self.state = None
        '''
        设置state变量记录当前进度：
        0 - 只有参数已确定
        1 - 所有索引页面URL解析完成
        2 - 所有图片下载信息解析完成
        3 - 图片下载信息已筛选，并可能存在已经下载结束的图片
        '''

    
    # 将args/class转化为字典
    def args_to_dict(self, args):
        dict_args = {}
        for arg in vars(args):
            dict_args[arg] = getattr(args, arg)

        self.dict_args = dict_args
        return dict_args


    # 将字典转化为args
    def dict_to_args(self, dict_args):
        args = parse_args()
        for arg in vars(args):
            vars(args)[arg] = dict_args[arg]
            
        self.args = args
        return args


    # 将字典转化为指定class
    def dict_to_class(self, dict_args, class_type):
        args = class_type()
        for arg in vars(args):
            vars(args)[arg] = dict_args[arg]

        return args


    # 形成Json的进度文件
    def write_config(self):
        
        dict_args = self.args_to_dict(self.args)
        dump_str = {}
        
        dump_str['spider_type'] = self.spider_type
        dump_str['args'] = dict_args 

        state = 0

        if self.page_urls is not None:
            state = 1
            dump_str['page_urls'] = self.page_urls
            
        if self.pic_infos is not None:
            state = 2
            dict_pic_infos = []
            for pic_info in self.pic_infos:
                dict_pic_infos.append(self.args_to_dict(pic_info))
            dump_str['pic_infos'] = dict_pic_infos            

        if self.filtered_pic_infos is not None:
            state = 3
            dict_filtered_pic_infos = []
            for filtered_pic_info in self.filtered_pic_infos:
                dict_filtered_pic_infos.append(self.args_to_dict(filtered_pic_info))
            dump_str['filtered_pic_infos'] = dict_filtered_pic_infos
        
        dump_str['state'] = state
        self.state = state
        self.json_str = json.dumps(
            dump_str, 
            indent=4, separators=(',', ': '), 
            ensure_ascii=False
        )
        
        # 一旦生成，自动输出至文件
        self.write_json_config(json_str = self.json_str)
        return self.json_str


    # 输出Json至文件
    def write_json_config(self, json_str, json_name=None):
        if json_name is None:  # 设置默认配置文件名
            json_name = self.begin_time + ' '.join(self.args.keywords) + ' config'

        with open(os.path.join(self.args.path, f'{json_name}.json'), 'w+') as f:
            f.write(json_str)

