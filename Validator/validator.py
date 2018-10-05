# coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""

import time
import gevent
import requests
from gevent             import pool
from gevent             import monkey
from DB.settings        import _DB_SETTINGS
from DB.settings        import _TABLE
from config.config      import CONCURRENCY
from config.config      import VALIDATE_AMOUNT
from config.config      import VALIDATE_F
from const.settings     import proxy_validate_url
from const.settings     import headers
from tools.threads      import ValidateStandbyThread
from Rator.rator        import Rator
from Helper.dbhelper    import Database


monkey.patch_socket()

class Validator(object):
    def __init__(self):
        self.db         = Database(_DB_SETTINGS)
        self.table      = _TABLE['standby']
        self.db.table   = self.table
        self.rator      = Rator(self.db)


    def standby_validate(self):
        while 1:
            gpool = pool.Pool(CONCURRENCY)
            gevent.joinall([gpool.spawn(self.validate_proxy, ':'.join([str(i),str(i)]),save=False) for i in range(1000)])
            time.sleep(VALIDATE_F)


    def run(self, proxyList):
        self.rator.begin()
        self.standbyThread = ValidateStandbyThread(self.standby_validate)
        # self.standbyThread.start()
        while 1:
            try:
                if proxyList:
                    pen = len(proxyList)
                    pop_len =  pen if pen <= VALIDATE_AMOUNT else VALIDATE_AMOUNT
                    stanby_proxies =[proxyList.pop() for x in range(pop_len)]
                    gpool = pool.Pool(CONCURRENCY)
                    gevent.joinall([gpool.spawn(self.validate_proxy,i) for i in stanby_proxies if i])
                time.sleep(VALIDATE_F)
            except Exception as e:
                self.rator.end()
                # self.standbyThread.join()
                raise e

    def validate_proxy(self,proxy,save=True):
        ip, port = proxy.split(':')
        proxy = {}
        try:
            response = requests.get(proxy_validate_url.format(ip,port),
                                    proxies = proxy,
                                    headers=headers,
                                    timeout=10)
        except Exception as e:
            print(e)
        else:
            data = response.json()
            res = data['msg'][0]
            if 'anony' in res and 'time' in res:

                bullet = {'ip':ip,'port':port,'anony_type':res['anony'],
                          'address':'','score':'','valid_time':'',
                          'resp_time':res['time'],'test_count':0,
                          'fail_count':0,'success_rate':''}
                if save:
                    self.rator.mark_success(bullet)
                else:
                    self.rator.mark_update(bullet)
                # print('sdata:%s'%str(data)+' 耗时:%.3f'%elapsed )
            else:
                if not save:
                    self.rator.mark_fail({'ip':ip,'port':port})



