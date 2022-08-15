import argparse
import os



# 解析爬虫参数
def parse_args():
    parser = argparse.ArgumentParser(description="# ================== Help ================== #")

    parser.add_argument('--kw', type=str, default="", dest="keywords", help="Input keywords; Multiple keywords are separated with ',' symbol")
    parser.add_argument('--skip-kw', type=str, default="", dest="filtered_keywords", help="Input keywords to skip; Multiple keywords are separated with ',' symbol")
    parser.add_argument('--start-page', type=int, default=1, help="First page number")
    parser.add_argument('--finish-page', type=int, default=-1, help="Last page number. Default set to -1 for the last available page")

    parser.add_argument('-no-s', action="store_true", dest="if_no_safe", help="Not downloading safe pictures")
    parser.add_argument('-no-q', action="store_true", dest="if_no_questionable", help="Not downloading questionable pictures")
    parser.add_argument('-no-e', action="store_true", dest="if_no_explicit", help="Not downloading explicit pictures")
    parser.add_argument('--score', type=int, default=0, dest="min_score", help="Lowest rating score")
    
    parser.add_argument('--t', type=float, default=10.0, dest="delay_time", help="Delay time between downloading threads (in seconds)")
    parser.add_argument('-r', action="store_true", dest="if_randomize_time", help="Randomize delay time. Current delay time will be the upper limit.")
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


# 显示当前参数，返回参数总数+1和参数序数对照参数名字典
def display_info(args):
    arg_num_pair = {}
    print("# ============== Spider Config ============== #")
    i = 1
    for arg in vars(args):
        print('%-3s'%(str(i) + '.'), '%-25s %s'%(arg, getattr(args, arg)))
        arg_num_pair[i] = arg
        i += 1
    print("===============================================")
    return i, arg_num_pair
    


# 显示并调整当前参数
def info_config(args):
    args.keywords = keywords_parse(args.keywords)
    args.filtered_keywords = keywords_parse(args.filtered_keywords)
    os.system("cls")

    while True:
        i, arg_num_pair = display_info(args)

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
            if arg_str == 'path':
                if len(new_arg.strip()) > 0:  # 字符串非空才更新路径
                    vars(args)[arg_str] = new_arg
            else:
                vars(args)[arg_str] = new_arg
            break


# 更新所有参数
def update_all_arg(args):
    print("Use T/F for boolean, keywords separated with ','.")
    for arg in vars(args):
        input_hint_str = f"Please input a new argument for {arg}:"
        update_arg(args, arg, type(getattr(args, arg)), input_hint_str)