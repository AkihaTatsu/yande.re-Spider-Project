import logging
import getpass
import sys
import os
import io
from io import StringIO
import datetime
from pathlib import Path



class Log():
    def __init__(self, path):
        if not Path(path).exists():
            os.makedirs(path)

<<<<<<< Updated upstream:Mylog.py
class Mylog(object):
	# 类Mylog的构造函数
	def __init__(self):
		self.user = getpass.getuser()
		self.logger = logging.getLogger(self.user)
		self.logger.setLevel(logging.DEBUG)

		# 日志文件名
		self.logFile = sys.argv[0][0:-3]+'.log'
		self.formatter = logging.Formatter('%(asctime)-12s %(levelname)-8s %(name)-10s %(message)-12s\r\n')

		# 日志输出到相关文件内
		self.logHand = logging.FileHandler(self.logFile, encoding='utf8')
		self.logHand.setFormatter(self.formatter)
		self.logHand.setLevel(logging.DEBUG)
		
		
		# self.logHandSt = logging.StreamHandler()
		# self.logHandSt.setFormatter(self.formatter)
		# self.logHandSt.setLevel(logging.DEBUG)
		

		self.logger.addHandler(self.logHand)
		# self.logger.addHandler(self.logHandSt)

	# 日志的五个级别
	def debug(self, msg):
		self.logger.debug(msg)
			
	def info(self, msg):
		self.logger.info(msg)
	
	def warn(self, msg):
		self.logger.warn(msg)

	def error(self, msg):
		self.logger.error(msg)

	def critical(self, msg):
		self.logger.critical(msg)
=======
        self.user = getpass.getuser()
        self.logger = logging.getLogger(self.user)
        self.logger.setLevel(logging.DEBUG)

        # 日志文件名
        self.logFile = os.path.join(path, datetime.datetime.now().strftime('%Y-%m-%d %H_%M_%S Log') + '.log')
        self.formatter = logging.Formatter('%(asctime)-12s %(levelname)-8s %(name)-10s %(message)-12s')

        # 日志输出到相关文件内
        self.logHand = logging.FileHandler(self.logFile, encoding='utf8')
        self.logHand.setFormatter(self.formatter)
        self.logHand.setLevel(logging.DEBUG)

        self.logger.addHandler(self.logHand)

    '''日志的五个级别'''
    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
>>>>>>> Stashed changes:Log.py


'''日志测试'''
if __name__ == '__main__':
<<<<<<< Updated upstream:Mylog.py
	mylog = Mylog()
	mylog.debug(u'Debug Message Test: 中文调试测试')
	mylog.info(u'Info Message Test: 中文信息测试')
	mylog.warn(u'Warn Message Test: 中文警告测试')
	mylog.error(u'Error Message Test: 中文错误测试')
	mylog.critical(u'Critical Message Test: 中文关键错误测试')


=======
    mylog = Log("D:\\")
    mylog.debug(u'Debug Message Test: 中文调试测试')
    mylog.info(u'Info Message Test: 中文信息测试')
    mylog.warning(u'Warn Message Test: 中文警告测试')
    mylog.error(u'Error Message Test: 中文错误测试')
    mylog.critical(u'Critical Message Test: 中文关键错误测试')
>>>>>>> Stashed changes:Log.py
