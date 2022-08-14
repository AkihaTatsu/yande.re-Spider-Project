import argparse
import sys
import os
from Spider_Framework import Yandere_Spider_Framework



def parse_args():
    parser = argparse.ArgumentParser(description="# ================== Help ================== #")

    parser.add_argument('--words', type=str, default="", dest="keywords", help="Input keywords; Multiple keywords are separated with ',' symbol")
    parser.add_argument('--skip-words', type=str, default="", dest="filtered_keywords", help="Input keywords to skip; Multiple keywords are separated with ',' symbol")
    parser.add_argument('--start-page', type=int, default=1, help="First page number")
    parser.add_argument('--finish-page', type=int, default=-1, help="Last page number. Default set to -1 for the last available page")

    parser.add_argument('-no-s', action="store_true", dest="if_no_safe", help="Not downloading safe pictures")
    parser.add_argument('-no-q', action="store_true", dest="if_no_questionable", help="Not downloading questionable pictures")
    parser.add_argument('-no-e', action="store_true", dest="if_no_explicit", help="Not downloading explicit pictures")
    parser.add_argument('--score', type=int, default=0, dest="min_score", help="Lowest rating score")
    
    parser.add_argument('--t', type=float, default=10.0, dest="delay_time", help="Delayed time between downloading threads (in seconds)")
    parser.add_argument('-r', action="store_true", dest="if_randomize_time", help="Randomize delayed time")
    parser.add_argument('--thread-num', type=int, default=5, help="Number of downloading threads")
    parser.add_argument('--proxy-type', type=str, default='', help="Proxy type (e.g. https)")
    parser.add_argument('--proxy', type=str, default='', help="Proxy setting (e.g. http://127.0.0.1:1080)")

    parser.add_argument('--path', type=str, default=os.path.join(os.getcwd(), 'DOWNLOAD'), help="Path of downloaded pictures")

    return parser.parse_args()


# 解析关键词为合法内容
def keywords_parse(key_str):
    new_str = key_str.lower().split(',')
    while '' in new_str:
        new_str.remove('')
    for i in range(len(new_str)):
        new_str[i] = new_str[i].strip().replace(' ', '_')
    return new_str


# 显示并调整当前参数
def info_display(args):
    args.keywords = keywords_parse(args.keywords)
    args.filtered_keywords = keywords_parse(args.filtered_keywords)
    os.system("cls")

    while True:
        arg_num_pair = {}

        print("# ============== Spider Config ============== #")
        i = 1
        for arg in vars(args):
            print('%-3s'%(str(i) + '.'), '%-25s %s'%(arg, getattr(args, arg)))
            arg_num_pair[i] = arg
            i += 1
        print("===============================================")

        num = '0'
        while len(args.keywords) <= 0 or not (num.isdigit() and 0 < int(num) < i):
            num = input("Input a number to change certain argument, # to change all, or press enter to continue:")
            if num.isdigit() and 0 < int(num) < i:
                input_hint_str = f"Please input a new argument for {arg_num_pair[int(num)]}.\nUse T/F for boolean, keywords separated with ',':"
                update_arg(args, arg_num_pair[int(num)], type(getattr(args, arg_num_pair[int(num)])), input_hint_str)
                os.system("cls")
                break
            elif num == '#':
                update_all_arg(args)
                os.system("cls")
                break
            elif len(args.keywords) == 0:
                print("At least 1 keyword is required.")
            else:
                return args


# 更新参数
def update_arg(args, arg_str, arg_type, input_hint_str):
    while True:
        new_arg = input(input_hint_str)
        if arg_type is int:
            try:
                vars(args)[arg_str] = int(new_arg)
                break
            except:
                print("Invalid input.")
        elif arg_type is float:
            try:
                vars(args)[arg_str] = float(new_arg)
                break
            except:
                print("Invalid input.")
        elif arg_type is bool:
            if new_arg == 'T' or new_arg == 't':
                vars(args)[arg_str] = True
                break
            elif new_arg == 'F' or new_arg == 'f':
                vars(args)[arg_str] = False
                break
            else:
                print("Invalid input.")
        elif arg_type is list:
            vars(args)[arg_str] = keywords_parse(new_arg)
            break
        elif arg_type is str:
            vars(args)[arg_str] = new_arg
            break

# 更新所有参数
def update_all_arg(args):
    print("Use T/F for boolean, keywords separated with ','.")
    for arg in vars(args):
        input_hint_str = f"Please input a new argument for {arg}:"
        update_arg(args, arg, type(getattr(args, arg)), input_hint_str)



def main_spider(args):
    spider = Yandere_Spider_Framework(args)
    # spider.connection_test()
    spider.get_page_urls()
    spider.get_page_html(spider.page_urls)
    spider.parse_pic_infos(spider.page_html_contents)
    spider.filter_pic_infos()
    spider.download_pics(spider.filtered_pic_infos)


if __name__ == '__main__':
    args = parse_args()
    args = info_display(args)
    main_spider(args)

