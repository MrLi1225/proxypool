'''日志模块'''

import logging
import os

from config.path import *

class Logger:
    def __init__(self, log_name='app_log', log_level=logging.DEBUG, log_dir=LOGS_DIR):
        # 创建日志文件夹，如果不存在
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.log_name = log_name
        self.log_level = log_level
        self.log_dir = log_dir
        self.logger = logging.getLogger(self.log_name)
        self.logger.setLevel(self.log_level)

        # 创建日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 创建文件处理器，输出到日志文件，指定编码为utf-8
        file_handler = logging.FileHandler(os.path.join(self.log_dir, f'{log_name}.log'), encoding='utf-8',mode='w')
        file_handler.setFormatter(formatter)

        # 创建控制台处理器，输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # 添加处理器到logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def log(self, level, message):
        if level == 'DEBUG':
            self.logger.debug(message)
        elif level == 'INFO':
            self.logger.info(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        elif level == 'ERROR':
            self.logger.error(message)
        elif level == 'CRITICAL':
            self.logger.critical(message)

    def set_level(self, level):
        """
        设置日志记录的级别
        """
        level_dict = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        self.logger.setLevel(level_dict.get(level.upper(), logging.DEBUG))


# 使用示例
if __name__ == "__main__":
    log = Logger(log_name='my_app', log_level=logging.DEBUG)

    log.log('DEBUG', 'This is a debug message 😀')
    log.log('INFO', 'This is an info message')
    log.log('WARNING', 'This is a warning message')
    log.log('ERROR', 'This is an error message')
    log.log('CRITICAL', 'This is a critical message 💥')
