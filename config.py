'''config'''
import os

MAIN_PATH = os.getcwd() + '\\'
ROOT_PATH = 'g:\\AutoMakeTest\\'
WORK_DIR = 'AutoBuildDir2'
BUILD_DIR = '_BUILD'
FINAL_DIR = '_FINAL'
OUTFILES_PATH = 'D:\\soft\\xampp-win32-5.5.28-0-VC11\\xampp\\htdocs\\outfiles\\'
WEB_OUTFILES_PATH = '../outfiles/'

RUNNING_ERRLOG = ROOT_PATH + 'running_errlog.txt'
COMPILE_ERRLOG = ROOT_PATH + 'compile_errlog.txt'
SHOW_ERRLOG_NAME = 'errlog.log'
RUNNING_LOG = ROOT_PATH + 'log.txt'


MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'buildserver'
MYSQL_USER = 'root'
MYSQL_PASSWD = ''
