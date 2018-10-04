# coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""
import json
import random
import gevent
import requests
from gevent import monkey,pool
monkey.patch_socket()
import time
from settings import proxy_validate_url
from settings import headers



class Validator(object):
    def __init__(self):
        pass

    def run(self, proxyList):
        while 1:
            if proxyList:
                gpool = pool.Pool(100)
                print('in validator:len = %d' % len(proxyList))
                gevent.joinall([gpool.spawn(self.validate_proxy,i) for i in proxyList if i])
                time.sleep(3)

    def validate_proxy(self,proxy):
        ip, port = proxy.split(':')
        try:
            response = requests.get(proxy_validate_url.format(ip,port),headers=headers,timeout=10)
        except Exception as e:
            print(e)
        else:
            data = response.json()
            print('sdata:%s'%str(data))
            gevent.sleep(random.randint(1,2)*0.01)
            return 'sssss'

