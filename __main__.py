'''auto make test'''
# import traceback
import shutil
import zipfile
import time
import os

from Database import MySQLClass
from MyLog import Logger

WORK_PATH = 'g:/AutoMakeTest/test/'
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306

LOG = Logger('g:/AutoMakeTest/log.txt')
DATABASE = MySQLClass(MYSQL_HOST, MYSQL_PORT)


def download_svn(url, ver, target_path):
    '''download_svn'''
    if os.path.exists(target_path):
        LOG.info('del {work_dir}'.format(work_dir=target_path))
        try:
            shutil.rmtree('{rm_path}'.format(rm_path=target_path))
        except PermissionError:
            LOG.record_except()
            return False
    LOG.info('dowmloading from {svn}'.format(svn=url))
    if os.system('svn export -r {0:d} {1:s} {2:s} > nul'.format(ver, url, target_path)) != 0:
        return False
    else:
        return True


def copy_file():
    '''copy automake.exe'''
    LOG.info('copy file...')
    try:
        shutil.copy('AutoMake.exe', '{dst_path}'.format(dst_path=WORK_PATH))
        shutil.copy('FileCmdJoint.exe', '{dst_path}'.format(dst_path=WORK_PATH))
    except PermissionError:
        LOG.record_except()
        return False
    return True


def build_makefile():
    '''build makefile'''
    LOG.info('build makefile...')
    if os.system('AutoMake.exe') != 0:
        return False
    else:
        return True


def do_compile():
    '''compile'''
    LOG.info('compiling...')
    start_time = time.time()
    os.system('cs-make clean --directory=_BUILD/ >nul')
    if os.system('cs-make all -j8 --directory=_BUILD/ 1>nul 2>error.txt') != 0:
        return False
    else:
        time_used = time.time() - start_time
        LOG.info('compile done, time used: %f seconds'%time_used)
        return True


def complete():
    '''creat update file and zip'''
    try:
        shutil.copy('_BUILD/rtos.bin', '{dst_path}'.format(dst_path=WORK_PATH))
    except PermissionError:
        LOG.record_except()
        return False
    if os.system('FileCmdJoint.exe') != 0:
        return False

    try:
        if os.path.exists('out/'):
            shutil.rmtree('out/')
        os.makedirs('out/升级程序/字库的U盘升级文件')
        os.makedirs('out/升级程序/应用的U盘升级文件')
        os.makedirs('out/烧片程序')
        os.makedirs('out/调试程序')
        os.makedirs('out/Flash寿命测试的U盘升级文件')
        for file in os.listdir():
            if os.path.splitext(file)[1] == '.sp4':
                LOG.info('copy {0}'.format(file))
                shutil.copy(file, 'out/升级程序/应用的U盘升级文件')
        for file in os.listdir('_BUILD/'):
            if os.path.splitext(file)[0] == 'rtos':
                LOG.info('copy {0}'.format(file))
                shutil.copy('_BUILD/{0}'.format(file), 'out/调试程序')
        shutil.copy('FLASH.bin', 'out/烧片程序')
        shutil.copy('tools/zk/update.sp4', 'out/升级程序/字库的U盘升级文件')
        # shutil.make_archive('out', 'tar', 'out/')  # 这个库会在zip根目录下多生成一个.目录
        os.chdir('out/')
        zip_file = zipfile.ZipFile('../out.zip', 'w', zipfile.ZIP_DEFLATED)
        for dirpath, _, filenames in os.walk('.'):
            for filename in filenames:
                zip_file.write(os.path.join(dirpath, filename))
        zip_file.close()
        os.chdir('../')
    except PermissionError:
        LOG.record_except()
        os.chdir('../')
        return False

    return True


def auto_build():
    '''start auto build'''
    try:
        DATABASE.connect()
    except PermissionError:
        LOG.record_except()
        LOG.error('connect database error!')
        input()
        exit(1)

    while True:
        try:
            data_row = DATABASE.one_target_row()
            if data_row:
                url = data_row['svn_url']
                ver = data_row['svn_version']
                build_id = data_row['buildid']
                LOG.info('auto build id:{id}'.format(id=build_id))
            else:
                time.sleep(5)
                continue
        except Exception:
            # LOG.record_except()
            LOG.record_except()
            return False

        DATABASE.set_build_start_flag(build_id)

        if download_svn(url, ver, WORK_PATH) is False:
            LOG.error('download svn error')
            DATABASE.set_build_end_flag(build_id, False)
            continue
        if copy_file() is False:
            LOG.error('copy file error')
            DATABASE.set_build_end_flag(build_id, False)
            continue
        os.chdir(WORK_PATH)
        if build_makefile() is False:
            LOG.error('build makefile error')
            DATABASE.set_build_end_flag(build_id, False)
            continue
        if do_compile() is False:
            LOG.error('compile error')
            DATABASE.set_build_end_flag(build_id, False)
            continue
        if complete() is False:
            LOG.error('complete error')
            DATABASE.set_build_end_flag(build_id, False)
            continue
        DATABASE.set_build_end_flag(build_id, True)
        LOG.info('auto build done')

if __name__ == '__main__':
    auto_build()
    LOG.error('error exit')
    exit(1)
