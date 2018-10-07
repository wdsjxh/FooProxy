#coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""


#采集器采集数据时间间隔
COLLECT_TIME_GAP    = 24*3600
#验证器的最大并发量
CONCURRENCY         = 200
#验证器一次取出多少条抓取的代理进行验证
VALIDATE_AMOUNT     = 500
#验证器验证抓取数据频率 ： 秒/次
VALIDATE_F          = 5
#验证器一次取出多少条本地库的代理进行验证
LOCAL_AMOUNT        = 1000
#验证器验证本地库频率 ： 秒/次
VALIDATE_LOCAL      = 300
#验证器请求超时重试次数
VALIDATE_RETRY      = 5
#代理IP成功率的最低要求,低于此要求均删除,100次周期测试
MIN_SUCCESS_RATE    = 0.2
#运行模式,置 1 表示运行，置 0 表示 不运行
#全置 0 表示只运行 API server
MODE = {
    'Collector' : 0,    #代理采集
    'Validator' : 0,    #验证存储
    'Rator'     : 1,    #打分存储
    'Detector'  : 0,    #高分检测
}
