import sqlite3 as sl
import logging

# 定义日志格式
# logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', filename='checkrun.log')  #, filename='checkrun.log'


# sqlite数据库操作
class DbHandler(object):
    def __init__(self):
        try:
            self.conn = sl.connect('note.db',check_same_thread=False)
        except Exception as e:
            print(e)
        else:
            self.cursor = self.conn.cursor()

    # 执行查询模块功能，并一次取出1条记录
    def select(self, sql, param=None):
        # print('param:',param)
        data = []
        if param is None:
            self.cursor.execute(sql)
        else:
            self.cursor.execute(sql, param)
        while True:
            rowdata = self.cursor.fetchone()
            if not rowdata:
                break
            else:
                data.append(rowdata)
        return data


    def alter(self, sql, param=None):
        '''
        # 增、删、改操作
        :param sql:
        :param param: 为元组类型数据结构
        :return:
        '''
        # print('传入参数',param)
        try:
            if param is None:
                self.cursor.execute(sql)
            else:
                self.cursor.execute(sql, param)
        except Exception as e:
            self.conn.rollback()
            print(e)
        else:
            self.conn.commit()

    # 退出时关闭游标及连接
    def __del__(self):
        self.cursor.close()
        self.conn.close()
