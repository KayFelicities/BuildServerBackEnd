'''auto make test'''
import traceback
import shutil
import zipfile
import time
import os
# import time

WORK_PATH = 'g:/AutoMakeTest/test/'
SVN_URL = 'file:///G:/MySVN/trunk/SP5_bz'
SVN_VER = 21


def download_svn(url, ver, target_path):
    '''download_svn'''
    if os.path.exists(target_path):
        print('del {work_dir}'.format(work_dir=target_path))
        try:
            shutil.rmtree('{rm_path}'.format(rm_path=target_path))
        except PermissionError:
            traceback.print_exc()
            return False
    print('dowmloading from {svn}'.format(svn=url))
    if os.system('svn export -r {0:d} {1:s} {2:s} > nul'.format(ver, url, target_path)) != 0:
        return False
    else:
        return True


def copy_file():
    '''copy automake.exe'''
    print('copy file...')
    try:
        shutil.copy('AutoMake.exe', '{dst_path}'.format(dst_path=WORK_PATH))
        shutil.copy('FileCmdJoint.exe', '{dst_path}'.format(dst_path=WORK_PATH))
    except PermissionError:
        traceback.print_exc()
        return False
    return True


def build_makefile():
    '''build makefile'''
    print('build makefile...')
    if os.system('AutoMake.exe') != 0:
        return False
    else:
        return True


def do_compile():
    '''compile'''
    print('compiling...')
    start_time = time.time()
    os.system('cs-make clean --directory=_BUILD/ >nul')
    if os.system('cs-make all -j8 --directory=_BUILD/ 1>nul 2>error.txt') != 0:
        return False
    else:
        time_used = time.time() - start_time
        print('compile done, time used: %f seconds'%time_used)
        return True


def complete():
    '''creat update file and zip'''
    try:
        shutil.copy('_BUILD/rtos.bin', '{dst_path}'.format(dst_path=WORK_PATH))
    except PermissionError:
        traceback.print_exc()
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
        for file in os.listdir():
            if os.path.splitext(file)[1] == '.sp4':
                print('copy {0}'.format(file))
                shutil.copy(file, 'out/升级程序/应用的U盘升级文件')
        for file in os.listdir('_BUILD/'):
            if os.path.splitext(file)[0] == 'rtos':
                print('copy {0}'.format(file))
                shutil.copy('_BUILD/{0}'.format(file), 'out/调试程序')
        shutil.copy('FLASH.bin', 'out/烧片程序')
        shutil.copy('tools/zk/update.sp4', 'out/升级程序/字库的U盘升级文件')
        # shutil.make_archive('1', 'tar', 'out/')
        os.chdir('out/')
        zip_file = zipfile.ZipFile('../out.zip', 'w', zipfile.ZIP_DEFLATED)
        for dirpath, _, filenames in os.walk('.'):
            for filename in filenames:
                zip_file.write(os.path.join(dirpath, filename))
        zip_file.close()
        os.chdir('../')
    except PermissionError:
        traceback.print_exc()
        return False

    return True


if __name__ == '__main__':
    if download_svn(SVN_URL, SVN_VER, WORK_PATH) is False:
        print('download svn error')
        exit(1)
    if copy_file() is False:
        print('copy file error')
        exit(1)
    os.chdir(WORK_PATH)
    if build_makefile() is False:
        print('build makefile error')
        exit(1)
    if do_compile() is False:
        print('compile error')
        exit(1)
    if complete() is False:
        print('complete error')
        exit(1)
    print('done')
    exit(0)
