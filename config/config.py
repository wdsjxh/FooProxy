#coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""


#采集器采集数据时间间隔,单位：秒
COLLECT_TIME_GAP    = 3600*3
#验证器的最大并发量
CONCURRENCY         = 200
#验证器一次取出多少条 抓取的 代理进行验证
VALIDATE_AMOUNT     = 500
#验证器验证抓取数据频率 ： 秒/次
VALIDATE_F          = 5
#验证器一次取出多少条 本地库 的代理进行验证
LOCAL_AMOUNT        = 500
#验证器验证本地库频率 ： 秒/次
VALIDATE_LOCAL      = 60*1
#验证器请求超时重试次数
VALIDATE_RETRY      = 5
#检测器检测数据库的频率: 秒/次
DETECT_LOCAL        = 60*1
#检测器一次取出多少条有效库的代理进行筛选
DETECT_AMOUNT       = 1000
#检测器一次取出多少条高分稳定数据库的代理进行检测
DETECT_HIGH_AMOUNT  = 1000
#代理IP成功率的最低要求,低于此要求均删除,100次周期测试 0.2=20%
MIN_SUCCESS_RATE    = 0.2
#有效代理数据库数据转至高分稳定数据库的成功率最低要求 0.8=80%
#以及测试总数的最低要求
STABLE_MIN_RATE     = 0.8500
STABLE_MIN_COUNT    = 100
#运行模式,置 1 表示运行，置 0 表示 不运行
#全置 0 表示只运行 API server
MODE = {
    'Collector' : 0,    #代理采集
    'Validator' : 1,    #验证存储
    'Rator'     : 1,    #打分存储
    'Detector'  : 0,    #高分检测
}
