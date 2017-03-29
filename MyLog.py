'''log class'''
import logging

class Logger:
    '''logger class'''
    def __init__(self, path, cmd_level=logging.INFO, file_level=logging.INFO):
        '''init'''
        self.logger = logging.getLogger(path)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

        # 设置CMD日志
        cmd_log = logging.StreamHandler()
        cmd_log.setFormatter(fmt)
        cmd_log.setLevel(cmd_level)

        # 设置文件日志
        file_log = logging.FileHandler(path)
        file_log.setFormatter(fmt)
        file_log.setLevel(file_level)
        self.logger.addHandler(cmd_log)
        self.logger.addHandler(file_log)

    def debug(self, message):
        '''debug'''
        self.logger.debug(message)

    def info(self, message):
        '''info'''
        self.logger.info(message)

    def warning(self, message):
        '''warning'''
        self.logger.warning(message)

    def error(self, message):
        '''error'''
        self.logger.error(message)

    def record_except(self):
        '''except'''
        self.logger.exception("Exception Logged")

