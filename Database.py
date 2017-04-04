'''database class'''
import pymysql

class MySQLClass():
    '''mySQL class'''
    def __init__(self, mysql_host_ip, mysql_host_port):
        '''init'''
        self.hostip = mysql_host_ip
        self.hostport = mysql_host_port
        self.conn = None
        self.cursor = None

    def connect(self, database, user, passwd):
        '''connect MySQL'''
        self.conn = pymysql.connect(host=self.hostip, port=self.hostport,
                                    user=user, passwd=passwd, db=database, charset='utf8')
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def one_target_row(self):
        '''get one target row need to be built'''
        self.conn.commit()
        self.cursor.execute("SELECT * FROM build_information \
                             WHERE status!='ok' AND status!='error' ORDER BY build_id")
        return self.cursor.fetchone()

    def set_build_status(self, build_id, status):
        '''set me when starting auto build'''
        query = "UPDATE build_information \
                 SET status='{status}', start_time=NOW() WHERE build_id='{id}'"\
                .format(status=status, id=build_id)
        self.cursor.execute(query)
        self.conn.commit()

    def set_zip_url(self, build_id, url):
        '''set zip url for downloading'''
        self.cursor.execute("UPDATE build_information \
                    SET out_zip_url='{url}', finsh_time=NOW() WHERE build_id='{id}'"\
                .format(url=url, id=build_id))
        self.conn.commit()

    def set_err_log_url(self, build_id, url):
        '''set error log url for downloading'''
        self.cursor.execute("UPDATE build_information \
                    SET err_log_url='{url}', finsh_time=NOW() WHERE build_id='{id}'"\
                .format(url=url, id=build_id))
        self.conn.commit()

    def set_err_count(self, build_id, err_count):
        '''set error count'''
        self.cursor.execute("UPDATE build_information \
                    SET err_count='{count}' WHERE build_id='{id}'"\
                .format(count=err_count, id=build_id))
        self.conn.commit()

    def close_connect(self):
        '''close cursor and connection'''
        self.cursor.close()
        self.conn.close()
