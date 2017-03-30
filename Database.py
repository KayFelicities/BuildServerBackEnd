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

    def connect(self):
        '''connect MySQL'''
        self.conn = pymysql.connect(host=self.hostip, port=self.hostport,
                                    user='root', passwd='', db='kay', charset='utf8')
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    def one_target_row(self):
        '''get one target row need to be built'''
        self.conn.commit()
        self.cursor.execute("SELECT * FROM build_information \
                             WHERE status='' OR status='1' ORDER BY buildid")
        return self.cursor.fetchone()

    def set_build_start_flag(self, build_id):
        '''set me when starting auto build'''
        query = "UPDATE build_information SET status='1', start_time=NOW() WHERE buildid='{id}'"\
                .format(id=build_id)
        self.cursor.execute(query)
        self.conn.commit()

    def set_build_end_flag(self, build_id, is_successful):
        '''set me when ending auto build'''
        self.cursor.execute("UPDATE build_information \
                    SET status='{res}', finsh_time=NOW() WHERE buildid='{id}'"\
                .format(res='2' if is_successful else '3', id=build_id))
        self.conn.commit()

    def close_connect(self):
        '''close cursor and connection'''
        self.cursor.close()
        self.conn.close()
