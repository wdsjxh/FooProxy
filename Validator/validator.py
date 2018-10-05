# coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""

import time
import gevent
import requests
from config     import CONCURRENCY
from config     import VALIDATE_AMOUNT
from const.settings import proxy_validate_url
from const.settings import headers
from gevent     import pool
from gevent     import monkey

monkey.patch_socket()

class Validator(object):
    def __init__(self):
        pass

    def run(self, proxyList):
        while 1:
            if proxyList:
                pen = len(proxyList)
                # print('in validator:len = %d' % len(proxyList))
                pop_len =  pen if pen <= VALIDATE_AMOUNT else VALIDATE_AMOUNT
                stanby_proxies =[proxyList.pop() for x in range(pop_len)]
                # print('validate : %d'%len(stanby_proxies))
                gpool = pool.Pool(CONCURRENCY)
                gevent.joinall([gpool.spawn(self.validate_proxy,i) for i in stanby_proxies if i])
                time.sleep(3)

    def validate_proxy(self,proxy):
        ip, port = proxy.split(':')
        try:
            start = time.time()
            response = requests.get(proxy_validate_url.format(ip,port),headers=headers,timeout=10)
            end = time.time()
            elapsed = round(end -start,3)

        except Exception as e:
            print(e)
        else:
            data = response.json()
            print('sdata:%s'%str(data)+' 耗时:%.3f'%elapsed)

