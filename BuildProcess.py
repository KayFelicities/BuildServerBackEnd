'''process dirs and files(include SVN download)'''
import os
import shutil
import zipfile
import time
import config
from MyLog import Logger

BUILD_PROC_LOG = Logger('build', config.RUNNING_ERRLOG)

class BuildProc():
    '''file process class'''
    def __init__(self, data_row, work_path, outfiles_path):
        '''init'''
        self.work_path = work_path
        self.build_path = os.path.join(work_path, config.BUILD_DIR)
        self.final_path = os.path.join(work_path, config.FINAL_DIR)
        self.data = data_row
        self.show_files_path = os.path.join(outfiles_path,
                                            '{id:06d}'.format(id=self.data['build_id']))

    def create_show_files_dir(self):
        '''create show files dir'''
        try:
            if os.path.exists(self.show_files_path):
                shutil.rmtree(self.show_files_path)
                time.sleep(1)
            os.makedirs(self.show_files_path)
        except:
            BUILD_PROC_LOG.error('create dirs error')
            raise

    def svn_download(self):
        '''download_svn'''
        for _ in range(2):  # del twice to avoid root dir exist
            if os.path.isdir(self.work_path):
                BUILD_PROC_LOG.info('del ' + self.work_path)
                res = os.system('rd /s /q ' + self.work_path)
                print('rd res:', res)
        BUILD_PROC_LOG.info('downloading from {svn}'.format(svn=self.data['svn_url']))
        if os.system('svn export -r {0:d} {1:s} {2:s} > nul'
                     .format(self.data['svn_ver'], self.data['svn_url'], self.work_path)) != 0:
            BUILD_PROC_LOG.error('SVN download error')
            raise PermissionError

    def create_work_env(self):
        '''create environment'''
        try:
            if os.path.isdir(self.final_path):
                shutil.rmtree(self.final_path)
            os.makedirs(self.final_path)

            if os.path.isdir(os.path.join(self.final_path, 'out')):
                shutil.rmtree(os.path.join(self.final_path, 'out'))
            for c_dir in [r'out\升级程序\字库的U盘升级文件', r'out\升级程序\应用的U盘升级文件',
                          r'out\烧片程序', r'out\调试程序', r'out\Flash寿命测试的U盘升级文件']:
                os.makedirs(os.path.join(self.final_path, c_dir))
            shutil.copy(os.path.join(config.MAIN_PATH, r'copys\AutoMake.exe'), self.work_path)
            shutil.copy(os.path.join(config.MAIN_PATH, r'copys\FileCmdJoint.exe'), self.final_path)
        except (PermissionError, OSError):
            BUILD_PROC_LOG.record_except()
            raise

        readme_file = '--FILE INFO--\n'
        for info in ['build_id', 'svn_url', 'svn_ver', 'release_ver', 'show_ver',
                     'kernel_ver', 'meter_ver', 'oem_ver', 'boot_type', 'boot_size',
                     'app_size', 'build_note', 'user_name', 'user_ip', 'commit_time']:
            readme_file += info + ': {content}\n'.format(content=self.data[info])
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
        .format(ShowVer=self.data['show_ver'], BspVer=self.data['bsp_ver'],
                KernelVer=self.data['kernel_ver'], MeterVer=self.data['meter_ver'],
                OemVer=self.data['oem_ver'], boot_file=self.data['boot_type'],
                boot_file_max_size=self.data['boot_size'], app_file_max_size=self.data['app_size'])
        try:
            with open(os.path.join(self.final_path, 'README.txt'), 'w', encoding='gb2312') as file:
                file.write(readme_file)
            with open(os.path.join(self.final_path, 'FileCmdJoint.ini'),
                      'w', encoding='utf-8') as file:
                file.write(filecmdjoint_file)
        except IOError:
            BUILD_PROC_LOG.record_except()
            raise

    def __build_makefile(self, build_args=''):
        '''build makefile'''
        BUILD_PROC_LOG.info('build makefile...')
        os.chdir(self.work_path)
        res = os.system('AutoMake.exe ' + build_args)
        os.chdir(config.MAIN_PATH)
        if res != 0:
            return False
        else:
            return True

    def do_compile(self):
        '''compile'''
        start_time = time.time()
        self.__build_makefile()
        BUILD_PROC_LOG.info('cs-make clean...')
        os.system('cs-make clean --directory={build_path} >nul'.format(build_path=self.build_path))
        BUILD_PROC_LOG.info('cs-make all...')
        if os.system('cs-make all -j8 --directory={build_path} 1>nul 2>>{errlog}'\
                    .format(build_path=self.build_path, errlog=config.COMPILE_ERRLOG)) != 0:
            BUILD_PROC_LOG.error('normal compile error')
            raise Exception
        time_use = time.time() - start_time
        BUILD_PROC_LOG.info('normal compile ok, time use: {tm:.2f} seconds'.format(tm=time_use))

        try:
            for file in [os.path.join(self.build_path, 'rtos.bin'),
                         os.path.join(self.build_path, 'rtos.elf'),
                         os.path.join(self.build_path, 'rtos.map')]:
                shutil.copy(file, self.final_path)
            shutil.copy(os.path.join(config.MAIN_PATH, 'copys', self.data['boot_type'])
                        , self.final_path)
        except (PermissionError, OSError):
            BUILD_PROC_LOG.record_except()
            raise

        os.chdir(self.final_path)
        res = os.system('FileCmdJoint.exe')
        os.chdir(config.MAIN_PATH)
        if res != 0:
            BUILD_PROC_LOG.error('FileCmdJoint error')
            raise Exception

        try:
            for file in os.listdir(self.final_path):
                if os.path.splitext(file)[1] == '.sp4':
                    BUILD_PROC_LOG.info('copy ' + file)
                    shutil.copy(os.path.join(self.final_path, file),
                                os.path.join(self.final_path, r'out\升级程序\应用的U盘升级文件'))
                    break
            else:
                BUILD_PROC_LOG.error('sp4 file not found!')
                raise Exception
            for file in os.listdir(self.final_path):
                if os.path.splitext(file)[0] == 'rtos':
                    BUILD_PROC_LOG.info('copy ' + file)
                    shutil.copy(os.path.join(self.final_path, file),
                                os.path.join(self.final_path, r'out\调试程序'))
            shutil.copy(os.path.join(self.final_path, 'FLASH.bin'),
                        os.path.join(self.final_path, r'out\烧片程序\%s.bin'%self.data['release_ver']))
            shutil.copy(os.path.join(config.MAIN_PATH, r'copys\zk.sp4'),
                        os.path.join(self.final_path, r'out\升级程序\字库的U盘升级文件\update.sp4'))
            shutil.copy(os.path.join(self.final_path, 'README.txt'),
                        os.path.join(self.final_path, 'out'))
        except (PermissionError, OSError):
            BUILD_PROC_LOG.record_except()
            raise

        # Flash test build
        start_time = time.time()
        self.__build_makefile('-DINCLUDE_FLASH_TEST')
        BUILD_PROC_LOG.info('cs-make clean...')
        os.system('cs-make clean --directory={build_path} >nul'.format(build_path=self.build_path))
        BUILD_PROC_LOG.info('cs-make all...')
        if os.system('cs-make all -j8 --directory={build_path} 1>nul 2>>{errlog}'\
                    .format(build_path=self.build_path, errlog=config.COMPILE_ERRLOG)) != 0:
            BUILD_PROC_LOG.error('flash test compile error')
            raise Exception
        time_use = time.time() - start_time
        BUILD_PROC_LOG.info('Flash test compile ok, time use: {tm:.2f} seconds'.format(tm=time_use))

        try:
            shutil.copy(os.path.join(self.build_path, 'rtos.bin'), self.final_path)
        except (PermissionError, OSError):
            BUILD_PROC_LOG.record_except()
            raise

        os.chdir(self.final_path)
        res = os.system('FileCmdJoint.exe')
        os.chdir(config.MAIN_PATH)
        if res != 0:
            BUILD_PROC_LOG.error('FileCmdJoint error')
            raise Exception
        for file in os.listdir(self.final_path):
            if os.path.splitext(file)[1] == '.sp4':
                BUILD_PROC_LOG.info('copy ' + file)
                shutil.copy(os.path.join(self.final_path, file),
                            os.path.join(self.final_path, r'out\Flash寿命测试的U盘升级文件\update.sp4'))
                break
        else:
            BUILD_PROC_LOG.error('sp4 file not found!')
            raise Exception

    def do_pack(self):
        '''create zip'''
        os.chdir(os.path.join(self.final_path, 'out'))
        # shutil.make_archive('out', 'tar', 'out\\')  # 这个库会在zip根目录下多生成一个.目录
        zip_file = zipfile.ZipFile(os.path.join(self.final_path, 'out.zip'),
                                   'w', zipfile.ZIP_DEFLATED)
        for dirpath, _, filenames in os.walk('.'):
            for filename in filenames:
                zip_file.write(os.path.join(dirpath, filename))
        zip_file.close()
        os.chdir(config.MAIN_PATH)
        try:
            shutil.copy(os.path.join(self.final_path, 'out.zip'),
                        os.path.join(self.show_files_path, self.data['release_ver'] + '.zip'))
        except (PermissionError, OSError):
            BUILD_PROC_LOG.record_except()
            raise

    def show_errlog(self):
        '''copy errlog'''
        shutil.copy(config.RUNNING_ERRLOG,
                    os.path.join(self.show_files_path, config.SHOW_ERRLOG_NAME))
        with open(config.COMPILE_ERRLOG, encoding='gb2312', errors='ignore') as file:
            compile_err_text = file.read()
        with open(os.path.join(self.show_files_path, config.SHOW_ERRLOG_NAME), 'a+') as file:
            file.write(compile_err_text)

    def final(self):
        '''clean files'''
        os.chdir(config.MAIN_PATH)
        # todo: del files
