'''auto make test'''
# import traceback
import shutil
import zipfile
import time
import os

from Database import MySQLClass
from MyLog import Logger

MAIN_PATH = os.getcwd() + '\\'
ROOT_PATH = 'g:\\AutoMakeTest\\'
WORK_PATH = ROOT_PATH + 'AutoBuildDir2\\'
BUILD_PATH = WORK_PATH + '_BUILD\\'
FINAL_PATH = WORK_PATH + '_FINAL\\'
OUTFILES_PATH = 'D:\\soft\\xampp-win32-5.5.28-0-VC11\\xampp\\htdocs\\outfiles\\'
WEB_OUTFILES_PATH = '../outfiles/'

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'buildserver'
MYSQL_USER = 'root'
MYSQL_PASSWD = ''

LOG = Logger('g:\\AutoMakeTest\\log.txt')
DATABASE = MySQLClass(MYSQL_HOST, MYSQL_PORT)


def download_svn(url, ver, target_path):
    '''download_svn'''
    if os.path.exists(target_path):
        LOG.info('del {work_dir}'.format(work_dir=target_path))
        res = os.system('rd /s /q ' + target_path)
        print('rd res:', res)
    if os.path.exists(target_path):
        LOG.info('del {work_dir}'.format(work_dir=target_path))
        res = os.system('rd /s /q ' + target_path)
        print('rd res:', res)
    LOG.info('dowmloading from {svn}'.format(svn=url))
    if os.system('svn export -r {0:d} {1:s} {2:s} > nul'.format(ver, url, target_path)) != 0:
        return False
    else:
        return True


def create_dirs():
    '''create dirs'''
    try:
        if os.path.exists(FINAL_PATH):
            shutil.rmtree(FINAL_PATH)
        os.makedirs(FINAL_PATH)
    except (PermissionError, OSError):
        LOG.record_except()
        try:
            if os.path.exists(FINAL_PATH):
                shutil.rmtree(FINAL_PATH)
            os.makedirs(FINAL_PATH)
        except (PermissionError, OSError):
            LOG.record_except()
            return False
    return True


def copy_file():
    '''copy automake.exe'''
    LOG.info('copy file...')
    try:
        shutil.copy(MAIN_PATH + 'AutoMake.exe', WORK_PATH)
        shutil.copy(MAIN_PATH + 'FileCmdJoint.exe', FINAL_PATH)
    except (PermissionError, OSError):
        LOG.record_except()
        return False
    return True


def build_makefile(args):
    '''build makefile'''
    LOG.info('build makefile...')
    os.chdir(WORK_PATH)
    if os.system('AutoMake.exe ' + args) != 0:
        os.chdir(ROOT_PATH)
        return False
    else:
        os.chdir(ROOT_PATH)
        return True


def do_compile():
    '''compile'''
    LOG.info('compiling...')
    start_time = time.time()
    os.system('cs-make clean --directory={build_path} >nul'.format(build_path=BUILD_PATH))
    if os.system('cs-make all -j8 --directory={build_path} 1>nul 2>{final_path}error.log'\
                 .format(build_path=BUILD_PATH, final_path=FINAL_PATH)) != 0:
        return False
    else:
        time_used = time.time() - start_time
        LOG.info('compile done, time used: {tm:.2f} seconds'.format(tm=time_used))
        return True


def prepare_out_files():
    '''creat update files, prepare dirs'''
    try:
        for file in [BUILD_PATH + 'rtos.bin', BUILD_PATH + 'rtos.elf', BUILD_PATH + 'rtos.map']:
            shutil.copy(file, FINAL_PATH)
        shutil.copytree(WORK_PATH + 'boot\\', FINAL_PATH + 'boot\\')
    except (PermissionError, OSError):
        LOG.record_except()
        return False

    os.chdir(FINAL_PATH)
    if os.system('FileCmdJoint.exe') != 0:
        return False

    try:
        if os.path.exists('out\\'):
            shutil.rmtree('out\\')
        os.makedirs('out\\升级程序\\字库的U盘升级文件')
        os.makedirs('out\\升级程序\\应用的U盘升级文件')
        os.makedirs('out\\烧片程序')
        os.makedirs('out\\调试程序')
        os.makedirs('out\\Flash寿命测试的U盘升级文件')
        for file in os.listdir():
            if os.path.splitext(file)[1] == '.sp4':
                LOG.info('copy ' + file)
                shutil.copy(file, 'out\\升级程序\\应用的U盘升级文件')
                break
        else:
            LOG.error('sp4 file not found!')
            return False
        for file in os.listdir():
            if os.path.splitext(file)[0] == 'rtos':
                LOG.info('copy ' + file)
                shutil.copy(file, 'out\\调试程序')
        shutil.copy(FINAL_PATH + 'FLASH.bin', 'out\\烧片程序')
        shutil.copy(WORK_PATH + 'tools\\zk\\update.sp4', 'out\\升级程序\\字库的U盘升级文件')
        shutil.copy(FINAL_PATH + 'README.txt', 'out\\')
        os.chdir(MAIN_PATH)
    except (PermissionError, OSError):
        LOG.record_except()
        os.chdir(MAIN_PATH)
        return False

    return True


def complete_flash_test():
    '''create flash test update file'''
    try:
        shutil.copy(BUILD_PATH + 'rtos.bin', FINAL_PATH)
    except (PermissionError, OSError):
        LOG.record_except()
        return False

    os.chdir(FINAL_PATH)
    if os.system('FileCmdJoint.exe') != 0:
        return False
    for file in os.listdir():
        if os.path.splitext(file)[1] == '.sp4':
            LOG.info('copy ' + file)
            shutil.copy(file, 'out\\Flash寿命测试的U盘升级文件\\update.sp4')
            break
    else:
        LOG.error('sp4 file not found!')
        return False
    return True


def create_readme_and_ini(data_row):
    '''create readme.txt and filecmdjoint.ini'''
    readme_file = '--FILE INFO--\n'
    for key in data_row:
        readme_file += str(key) + ':\n' + '{content}\n\n'.format(content=data_row[key])
    filecmdjoint_file = \
    '''[cfg]
    #######U盘升级配置#######
    ShowVer = {ShowVer}
    BspVer = {BspVer}
    KernelVer = {KernelVer}
    MeterVer = {MeterVer}
    OemVer = {OemVer}

    #######文件拼接配置#######
    Files = 2
    Blank = 255
    OutFile = ./FLASH.bin
    [f1]
    FileName = {boot_file}
    FileMaxSize = {boot_file_max_size}
    [f2]
    FileName = rtos.bin
    FileMaxSize = {app_file_max_size}\n'''\
    .format(ShowVer=data_row['show_ver'], BspVer=data_row['bsp_ver'],
            KernelVer=data_row['kernel_ver'], MeterVer=data_row['meter_ver'],
            OemVer=data_row['oem_ver'], boot_file=data_row['boot_type'],
            boot_file_max_size=data_row['boot_size'], app_file_max_size=data_row['app_size'])
    try:
        with open(FINAL_PATH + 'README.txt', 'w', encoding='utf-8') as file:
            file.write(readme_file)
        with open(FINAL_PATH + 'FileCmdJoint.ini', 'w', encoding='utf-8') as file:
            file.write(filecmdjoint_file)
    except IOError:
        LOG.record_except()
        return False
    return True


def create_zip():
    '''create zip'''
    os.chdir('out\\')
    # shutil.make_archive('out', 'tar', 'out\\')  # 这个库会在zip根目录下多生成一个.目录
    zip_file = zipfile.ZipFile(FINAL_PATH + 'out.zip', 'w', zipfile.ZIP_DEFLATED)
    for dirpath, _, filenames in os.walk('.'):
        for filename in filenames:
            zip_file.write(os.path.join(dirpath, filename))
    zip_file.close()
    os.chdir(MAIN_PATH)
    return True


def list_out_files(build_id, zip_name='out'):
    '''list zip and logs to database'''
    out_files_path = OUTFILES_PATH + '{id:06d}\\'.format(id=build_id)
    try:
        if os.path.exists(out_files_path):
            shutil.rmtree(out_files_path)
        os.makedirs(out_files_path)

        shutil.copy(FINAL_PATH + 'out.zip',
                    out_files_path + zip_name + '.zip')
        shutil.copy(FINAL_PATH + 'error.log', out_files_path)
    except (PermissionError, OSError):
        LOG.record_except()
        return False
    web_out_file_path = WEB_OUTFILES_PATH + '{id:06d}/'.format(id=build_id)
    DATABASE.set_zip_url(build_id, web_out_file_path + zip_name + '.zip')
    DATABASE.set_err_log_url(build_id, web_out_file_path + 'error.log')
    return True

def auto_build():
    '''start auto build'''
    try:
        DATABASE.connect(MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWD)
    except (PermissionError, OSError):
        LOG.record_except()
        LOG.error('connect database error!')
        input()
        exit(1)

    while True:
        try:
            data_row = DATABASE.one_target_row()
            if data_row:
                url = data_row['svn_url']
                ver = data_row['svn_ver']
                build_id = data_row['build_id']
                LOG.info('auto build id: {id}'.format(id=build_id))
                # list_out_files(build_id, zip_name=data_row['release_ver'])
                # create_readme_and_ini(data_row)
                # break
            else:
                time.sleep(5)
                continue
        except Exception:
            LOG.record_except()
            return False

        DATABASE.set_build_status(build_id, 'svn downloading')
        if download_svn(url, ver, WORK_PATH) is False:
            LOG.error('download svn error')
            DATABASE.set_build_status(build_id, 'svn err')
            continue
        if create_dirs() is False:
            LOG.error('create dirs error')
            DATABASE.set_build_status(build_id, 'create dir err')
            continue
        if copy_file() is False:
            LOG.error('copy file error')
            DATABASE.set_build_status(build_id, 'copy file err')
            continue
        if create_readme_and_ini(data_row) is False:
            LOG.error('create readme error')
            DATABASE.set_build_status(build_id, 'create ini err')
            continue

        DATABASE.set_build_status(build_id, 'compiling1')
        if build_makefile('') is False:
            LOG.error('build makefile error')
            DATABASE.set_build_status(build_id, 'automake1 err')
            continue
        if do_compile() is False:
            LOG.error('compile error')
            DATABASE.set_build_status(build_id, 'compile1 err')
            continue
        if prepare_out_files() is False:
            LOG.error('prepare out files error')
            DATABASE.set_build_status(build_id, 'copy1 err')
            continue

        DATABASE.set_build_status(build_id, 'compiling2')
        if build_makefile('-DINCLUDE_FLASH_TEST') is False:
            LOG.error('build makefile error')
            DATABASE.set_build_status(build_id, 'automake2 err')
            continue
        if do_compile() is False:
            LOG.error('compile error')
            DATABASE.set_build_status(build_id, 'compile2 err')
            continue
        if complete_flash_test() is False:
            LOG.error('complete flash test error')
            DATABASE.set_build_status(build_id, 'copy2 err')
            continue

        if create_zip() is False:
            LOG.error('create zip error')
            DATABASE.set_build_status(build_id, 'create zip err')
            continue

        if list_out_files(build_id, zip_name=data_row['release_ver']) is False:
            LOG.error('list_out_files error')
            DATABASE.set_build_status(build_id, 'create url err')
            continue

        DATABASE.set_build_status(build_id, 'ok')
        LOG.info('auto build done')

if __name__ == '__main__':
    auto_build()
    LOG.error('error exit')
    exit(1)
