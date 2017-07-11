# coding:utf-8
"""
Author:王吉亮
Date:20161027
"""

import MySQLdb,logging
from Lib.UsualTools import UsualTools
from Config.GlobalConf import ServiceConf
from Config.EncodeConf import MyEncode
import sys

class DBTool(object):
    """数据库处理类
    处理数据库相关操作
    """

    def __init__(self, host='', port=3306, username='', password='',db=''):
        self.__open = False
        if host != '':
            self.__host = host
            self.__port = port
            self.__username = username
            self.__password = password
            self.__db = db
            # logging.debug( u"DBTool.py: __init__: 数据库地址：%s。" % host )
            self.connect()

    def connect(self):
        if self.__open:
            return
        try:
            if self.__db =='':
                self.__conn = MySQLdb.connect(host=self.__host, port=self.__port, user=self.__username,
                                          passwd=self.__password, charset="utf8")
            else:
                self.__conn = MySQLdb.connect(host=self.__host, port=self.__port, db=self.__db, user=self.__username,
                                              passwd=self.__password, charset="utf8")
            self.__open = True
            # logging.debug( u"DBTool.py: connect: 数据库连接成功。")
        except Exception, e:
            logging.debug( u"DBTool.py: connect: FATAL_ERROR: 创建数据库连接失败[%s]，请检查数据库配置以及数据库可用性。数据库信息：Host:[%s] Port:[%s] User:[%s] Pass:[%s]" %(e,self.__host,self.__port,self.__username,self.__password))
            sys.exit(0)

    def release(self):
        if self.__open:
            self.__conn.close()
            self.__open = False
            # if self.__open == False:
            #     logging.debug( u"DBTool.py: release: 数据库连接连接断开。")

    def flush(self):
        self.release()
        self.connect()

    def execute_sql(self, sql):
        """执行sql语句
        :param sql: excel传入的sql.
        :return: 返回成功失败,只有所有的都成功才返回成功
        """
        try:
            self.connect()
            cursor = self.__conn.cursor()
            cursor.execute(sql)
            self.__conn.commit()
            data = cursor.fetchall()
            # 关闭数据库连接
            return data
        except Exception, e:
            logging.debug( u"DBTool.py: execute_sql : 发生异常：%s, 异常类型%s." % (e,type(e)))
            return e.args

    def get_effected_rows_count(self, sql):
        """执行sql语句

        :param sql: excel传入的sql.
        :return: 返回成功失败,只有所有的都成功才返回成功
        """
        sql = sql.strip()
        sql_lower = sql.lower()
        try:
            self.connect()
            cursor = self.__conn.cursor()
            curd_judge_string = sql_lower[0:6]
            #logging.debug(u"DBTool.py:get_effected_rows_count:curd_judge_string:[%s]" % curd_judge_string)
            if curd_judge_string == "select":
                #logging.debug(u"DBTool.py:get_effected_rows_count:INTO select.")
                cursor.execute(sql)
                #logging.debug(u"DBTool.py:get_effected_rows_count: SELECT影响行数：%d" % cursor.rowcount)
                return cursor.rowcount
            elif curd_judge_string == 'update':
                sql_lower = sql.lower().strip()
                where_loc = sql_lower.find('where')
                set_loc = sql_lower.find('set')
                table_name = sql[6:set_loc].strip()
                where_str = sql[where_loc + 5:].strip()
                if where_loc == -1:
                   return ServiceConf().sql_effect_lines+1
                new_sql =  "select * from %s where %s" % (table_name, where_str)
                cursor.execute(new_sql)
                return cursor.rowcount
            elif curd_judge_string == 'delete':
                # delete from tablename where where cb = 2  to select * from tablename where xxxxxx
                sql_lower = sql.lower().strip()
                from_loc = sql_lower.find('from')
                where_loc = sql_lower.find('where')
                table_name = sql[from_loc + 4:where_loc == -1 and len(sql) or where_loc + 1]
                where_str = sql[where_loc + 5:].strip()
                if where_loc == -1:
                   return ServiceConf().sql_effect_lines+1
                new_sql = "select * from %s where %s" % (table_name, where_str)
                cursor.execute(new_sql)
                return cursor.rowcount
            elif curd_judge_string == 'insert':
                return 1
            else:
                return -1
        # 关闭数据库连接
        except Exception, e:
            return -1


if __name__ == "__main__":
    pass
