# coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-05
"""
import pymongo
import logging
from inspect            import isfunction
from const.settings     import con_map

logger = logging.getLogger()

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
        连接MongoDB
        """
        self.conn = pymongo.MongoClient(self.host, self.port,username=self.user,password=self.passwd)
        self.handler = self.conn[self.db]

    def close(self):
        """
        关闭数据库连接
        """
        self.conn.close()
        self.conn=None

    def use_db(self,dbname):
        """
        连接数据库后使用名为dbname的数据库
        :param dbname: 要使用的数据库
        """
        self.handler = self.conn[dbname]

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
            self.handler[table].insert(data)
        elif isinstance(data,list):
            for i in data:
                if isinstance(i,dict):
                    i = format(i) if format else i
                    self.handler[table].insert(i)
                else:
                    raise TypeError('Expected a dict type value inside the list,%s type received.' % type(data))
        else:
            raise TypeError('Expected a [{},{}..] or {} type data,%s type received.' % type(data))

    def select(self,condition,tname=None):
        table = self.table if self.table else tname
        if not isinstance(condition,dict):
            raise TypeError('condition is not a valid dict type param.')
        else:
            try:
                conditions = self.gen_mapped_condition(condition)
                data = list(self.handler[table].find(conditions))
                return data if data else []
            except Exception as e:
                logger.error('Error class : %s , msg : %s ' % (e.__class__, e))
                return

    def delete(self,condition,tname=None):
        if not condition: return
        conditions = self.gen_mapped_condition(condition)
        table = self.table if self.table else tname
        if not isinstance(condition,dict):
            raise TypeError('condition is not a valid dict type param.')
        self.handler[table].delete_many(conditions)

    def update(self,condition,data,tname=None):
        table = self.table if self.table else tname
        if not data :return
        if not isinstance(condition, dict) and not isinstance(data,dict):
            raise TypeError('Params (condition and data) should both be the dict type.')
        conditions= self.gen_mapped_condition(condition)
        self.handler[table].update(conditions,{'$set':data},False,True )

    def all(self,tname=None):
        table = self.table if self.table else tname
        data = list(self.handler[table].find())
        return data

    def get_many(self,condition,num=1,tname=None):
        """
        获取查询条件结果的随机num条数据
        :param condition: 查询条件，{}表示所有
        :param num: 随机数据条数,默认1条
        :param tname: 集合名
        :return: 返回查询结果[{},{},...]
        """
        table = self.table if self.table else tname
        data = self.handler[table].find(condition).limit(num).skip()

    def gen_mapped_condition(self,condition):
        for key in condition:
            if isinstance(condition[key], dict):
                t = condition[key]
                operator = list(t.keys())[0]
                value = t[operator]
                o = con_map[operator]
                condition[key].pop(operator)
                condition[key][o] = value
        return condition


















