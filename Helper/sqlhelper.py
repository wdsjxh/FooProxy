# coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-05
"""
from gevent.exceptions import ConcurrentObjectUseError
from DB.settings import create_db_path,create_table_path

def exe_sql(conn,sql,back=False):
    cur = conn.cursor()
    try:
        a = [i + ';' for i in sql.split(';')][:-1]
        for i in a:
            cur.execute(i)
        conn.commit()
        if back:
            data = cur.fetchall()
            return data
    except (RuntimeError,BlockingIOError,ConcurrentObjectUseError) as e:
        # conn.rollback()
        pass
    except Exception as e:
        conn.rollback()
        raise  e

def gen_sql_insert(data,table):
    """
    为mysql生成插入的sql语句
    :param data:要插入的数据，dict类型，其key值与数据表一一对应
    :param table : 要插入的mysql数据表名
    :return: 生成的sql语句
    """
    val_len_str = ','.join(['{}' for x in range(len(data))])
    values = [i for i in data.keys()]
    res = []
    [res.append(i) for i in values]
    for i in values:
        if isinstance(data[i], str):
            res.append('"' + data[i] + '"')
        elif isinstance(data[i], list):
            res.append('"' + str(data[i]) + '"')
        elif data[i] == None:
            data[i] = False
            res.append(data[i])
        else:
            res.append(data[i])
    sql = "insert into %s(" % table + val_len_str + ') values(' + val_len_str + ');'
    try:
        sql = sql.format(*res)
    except Exception as e:
        raise e
    return sql

def use_db(conn,dbname,create):
    """

    :param conn:
    :param dbname:
    :param create:
    """
    sql_no = 'use {db};'.format(**{'db':dbname})
    sql_create = 'create database if not exists {db};use {db};'.format(**{'db':dbname})
    sql = sql_no if not create else sql_create
    try:
        exe_sql(conn,sql)
    except Exception as e:
        raise e

def save(conn,data,table):
    if not data:return
    sql = gen_sql_insert(data,table)
    try:
        exe_sql(conn,sql)
    except Exception as e:
        print(sql)

        raise e

def All(conn,table):
    sql = 'select * from {t};'.format(**{'t':table})
    try:
        data = exe_sql(conn,sql,back=True)
        return list(data)
    except Exception as e:
        raise e


def mysql_db_preparation(conn,dbname,table):
    """
    检测mysql数据库中是否存在代理池的数据库和数据表，根据代理池数据库设置查询
    如果存在，则检测数据库中是否存在设置中的数据表，存在则返回，不存在
    则创建一个新的代理池数据表。
    :param conn:数据库连接句柄
    :param dbname:数据库名
    :param table:数据表名
    """
    cur = conn.cursor()
    try:
        sql = "SELECT `TABLE_NAME` FROM `INFORMATION_SCHEMA`.`TABLES` " \
              "WHERE `TABLE_SCHEMA`='{db}' AND `TABLE_NAME`='{tname}' ;".format(
            **{'db': dbname, 'tname': table})
        cur.execute(sql)
        conn.commit()
        res = cur.fetchall()
        if not res:
            with open(create_db_path, 'r') as f:
                with open(create_table_path, 'r') as p:
                    sql = f.read().replace('\n', '')
                    sql += p.read().replace('\n', '')
            sql = sql.format(**{'db': dbname, 'table': table})
            a = [i + ';' for i in sql.split(';')][:-1]
            for i in a:
                cur.execute(i)
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e



