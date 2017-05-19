'''log class'''
import os
import logging
import config

class Logger:
    '''logger class'''
    def __init__(self, name, errlog_path, log_path=config.RUNNING_LOG, cmd_level=logging.INFO,
                 file_level=logging.INFO, errlog_level=logging.ERROR):
        '''init'''
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')

        cmd_log = logging.StreamHandler()
        cmd_log.setFormatter(fmt)
        cmd_log.setLevel(cmd_level)

        if not os.path.isdir(os.path.split(log_path)[0]):
            os.makedirs(os.path.split(log_path)[0])
        file_log = logging.FileHandler(log_path, encoding='utf-8')
        file_log.setFormatter(fmt)
        file_log.setLevel(file_level)

        err_log = logging.FileHandler(errlog_path, encoding='utf-8')
        err_log.setFormatter(fmt)
        err_log.setLevel(errlog_level)

        self.logger.addHandler(cmd_log)
        self.logger.addHandler(file_log)
        self.logger.addHandler(err_log)

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

