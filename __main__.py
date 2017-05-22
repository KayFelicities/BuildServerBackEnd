'''auto make test'''
import time
import os
import config
from BuildProcess import BuildProc
from MyLog import Logger
from Database import MySQLClass


LOG = Logger('main', config.RUNNING_ERRLOG)
DATABASE = MySQLClass(config.MYSQL_HOST, config.MYSQL_PORT)


def auto_build():
    '''start auto build'''
    try:
        DATABASE.connect(config.MYSQL_DATABASE, config.MYSQL_USER, config.MYSQL_PASSWD)
    except Exception:
        LOG.record_except()
        LOG.error('connect database error!')
        input()
        exit(1)

    while True:
        try:
            data_row = DATABASE.one_target_row()
        except Exception:
            LOG.record_except()
            LOG.error('connect database error!')
            time.sleep(300)
            continue
        if not data_row:
            time.sleep(5)
            continue

        build_id = data_row['build_id']
        web_out_file_path = config.WEB_OUTFILES_PATH + '{id:06d}/'.format(id=build_id)
        try:
            with open(config.RUNNING_ERRLOG, 'w') as file:
                file.write('ID-{id} running error:\n'.format(id=build_id))
            with open(config.COMPILE_ERRLOG, 'w') as file:
                file.write('\nID-{id} compile error:\n'.format(id=build_id))

            LOG.info('\n\n#'*7 + ' AUTO BUILD ' + '#'*7)
            LOG.info('starting build id {id}'.format(id=build_id))
            build_proc = BuildProc(data_row, os.path.join(config.ROOT_PATH, config.WORK_DIR)
                                   , config.OUTFILES_PATH)

            build_proc.create_show_files_dir()

            LOG.info('svn downloading...')
            DATABASE.set_build_status(build_id, 'svn downloading')
            build_proc.svn_download()
            LOG.info('svn download ok')

            LOG.info('creating work environment...')
            DATABASE.set_build_status(build_id, 'create work env')
            build_proc.create_work_env()
            LOG.info('creat work environment ok')

            LOG.info('compiling...')
            DATABASE.set_build_status(build_id, 'compiling')
            build_proc.do_compile()
            LOG.info('compile ok')

            LOG.info('packing...')
            DATABASE.set_build_status(build_id, 'packing')
            build_proc.do_pack()
            LOG.info('pack ok')

            build_proc.final()
            LOG.info('auto build done')
            DATABASE.set_build_status(build_id, 'ok')

        except Exception:
            build_proc.final()
            build_proc.show_errlog()
            DATABASE.set_build_status(build_id, 'error')

if __name__ == '__main__':
    auto_build()
    LOG.error('error exit')
    exit(1)
