'''config'''
import os

BUILD_TRY_MAX = 3

MAIN_PATH = os.getcwd() + '\\'
ROOT_PATH = r'g:\AutoMakeTest'
WORK_DIR = 'AutoBuildDir2'
BUILD_DIR = '_BUILD'
FINAL_DIR = '_FINAL'
OUTFILES_PATH = r'D:\soft\xampp-win32-5.5.28-0-VC11\xampp\htdocs\BuildServer\outfiles'
WEB_OUTFILES_PATH = '../outfiles/'

RUNNING_ERRLOG = os.path.join(ROOT_PATH, 'running_errlog.txt')
COMPILE_ERRLOG = os.path.join(ROOT_PATH, 'compile_errlog.txt')
SHOW_ERRLOG_NAME = 'errlog.log'
RUNNING_LOG = os.path.join(ROOT_PATH, 'log.txt')


MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'buildserver'
MYSQL_USER = 'root'
MYSQL_PASSWD = ''
