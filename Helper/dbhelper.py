# coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-05
"""
import pymysql
import pymongo
from inspect            import isfunction
from Helper.sqlhelper   import use_db,save,All
from Helper.sqlhelper   import mysql_db_preparation


from DB.settings import _DB_SETTINGS

class Database(object):

    def __init__(self,settings):
        self.host   = settings['host']
        self.port   = settings['port']
        self.user   = settings['user']
        self.passwd = settings['passwd']
        self.type   = settings['backend']
        self.db     = settings['database']
        self.conn    = None
        self.handler = None
        self.table   = None

    def connect(self):
        """
        根据初始化给定的settings中的backend来进行数据库的连接
        """
        try:
            return {
                'mongodb'   : self.__connect_mongodb,
                'mysql'     : self.__connect_mysql,
            }[str(self.type).lower()]()
        except KeyError:
            raise ValueError('No database backend [%s] is detected!' % (self.type))

    def close(self):
        """
        关闭数据库连接
        """
        if isinstance(self.handler, pymysql.cursors.Cursor):
            self.handler.close()
        self.conn.close()

    def __connect_mongodb(self):
        """
        连接MongoDB
        """
        self.conn = pymongo.MongoClient(self.host, self.port,username=self.user,password=self.passwd)
        self.handler = self.conn[self.db]

    def __connect_mysql(self):
        """
        连接mysql
        """
        self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd,database=self.db)
        self.handler = self.conn.cursor()

    def use_db(self,dbname,create=False):
        """
        连接数据库后使用名为dbname的数据库
        :param dbname: 要使用的数据库
        """
        if isinstance(self.conn,pymongo.MongoClient):
            self.handler = self.conn[dbname]
        elif isinstance(self.conn,pymysql.connections.Connection):
            use_db(self.conn,dbname,create)

    def save(self,data,tname=None,format=None):
        """
        保存数据到数据表|集合
        :param data: 要保存的数据,{}类型或 [{},{}..]类型
        :param tname: 数据表(mysql) 或 数据集(mongodb)
        :param format:对数据进行格式化的函数，可以根据数据结构自定义
        """
        table = self.table if self.table else tname
        format = None if not isfunction(format) else format
        if not table:
            raise Exception('No table or data collection specified by tname.')
        if isinstance(data,dict):
            data = format(data) if format else data
            if isinstance(self.conn, pymongo.MongoClient) :
                self.handler[table].insert(data)
            elif isinstance(self.conn,pymysql.connections.Connection):
                save(self.conn, data, table)
        elif isinstance(data,list):
            for i in data:
                if isinstance(i,dict):
                    i = format(i) if format else i
                    if isinstance(self.conn, pymongo.MongoClient) :
                        self.handler[table].insert(i)
                    elif isinstance(self.conn, pymysql.connections.Connection) :
                        save(self.conn, i, table)
                else:
                    raise TypeError('Expected a dict type value inside the list,%s type received.' % type(data))
        else:
            raise TypeError('Expected a [{},{}..] or {} type data,%s type received.' % type(data))

    def select(self):
        pass

    def delete(self):
        pass

    def all(self,tname=None):
        table = self.table if self.table else tname
        data  = []
        if isinstance(self.conn,pymongo.MongoClient):
            data = list(self.handler[table].find())
        elif isinstance(self.conn,pymysql.connections.Connection):
            data = All(self.conn,table)
        return data


    def make_preparation(self,tnames):
        if self.type == 'mysql':
            self.connect()
            for i in tnames:
                mysql_db_preparation(self.conn,self.db,i)
            self.close()




#
# db  = Database(_DB_SETTINGS)
# db.connect()
# a = db.all('ps')
# print(a)
# db.save({'ip':'127.0.0.1','port':'8080'},tname='ps')















