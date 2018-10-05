#coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""

#代理数据库拟存储的代理数据条目最大值
MAX_AMOUNT = 10**5
#去重的布隆过滤器误判率设置
ERROR_RATE = 0.001
#采集器采集数据时间间隔
COLLECT_TIME_GAP    = 24*3600
#验证器的最大并发量
CONCURRENCY         = 200
#验证器一次取出多少条抓取的代理进行验证
VALIDATE_AMOUNT     = 500
#验证器验证频率 ： 秒/次
VALIDATE_F          = 3
