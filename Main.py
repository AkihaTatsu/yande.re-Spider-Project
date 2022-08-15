from Command_Utils import parse_args, info_config
from Spider_Framework import Yandere_Spider_Framework
from Spider_Framework_Character import Yandere_Spider_Framework_Character



# 爬取主程序
def main_spider(args):
    spider = Yandere_Spider_Framework(args)
    # spider.connection_test()
    spider.get_page_urls()
    spider.get_page_html(spider.page_urls)
    spider.parse_pic_infos(spider.page_html_contents)
    spider.filter_pic_infos(spider.pic_infos)
    spider.download_pics(spider.filtered_pic_infos)


# 爬取主程序（角色）
def main_spider_char(args):
    spider = Yandere_Spider_Framework_Character(args)
    # spider.connection_test()
    spider.get_page_urls()
    spider.get_page_html(spider.page_urls)
    spider.parse_pic_infos(spider.page_html_contents)
    spider.filter_pic_infos(spider.pic_infos)
    spider.filtered_pic_infos = spider.get_pic_char_tags(spider.filtered_pic_infos)
    spider.download_pics(spider.filtered_pic_infos)
    spider.move_all_pictures(spider.filtered_pic_infos)

# 选择爬取类型
def select_spider(args):
    print('Select a spider type:', 
    '1. Basic', 
    '2. Classify by characters', sep='\n')
    spider_type = input('Input type number (# to exit):')
    while True:
        if spider_type == '1':
            main_spider(args)
            break
        elif spider_type == '2':
            main_spider_char(args)
            break
        elif spider_type == '#':
            break
        else:
            spider_type = input('Invalid type number. Please input again:')
            


if __name__ == '__main__':
    args = parse_args()
    args = info_config(args)
    select_spider(args)

