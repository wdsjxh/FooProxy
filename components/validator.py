# coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""

import time
import gevent
import requests
import logging
from gevent             import pool
from gevent             import monkey
from config.DBsettings import _DB_SETTINGS
from config.DBsettings import _TABLE
from config.config      import CONCURRENCY
from config.config      import VALIDATE_AMOUNT
from config.config      import VALIDATE_F
from const.settings     import proxy_validate_url
from const.settings     import headers
from config.config      import VALIDATE_RETRY
from components.rator import Rator
from components.dbhelper import Database
from requests.adapters  import HTTPAdapter

monkey.patch_socket()
logger = logging.getLogger('Validator')

class Validator(object):
    def __init__(self):
        self.db         = Database(_DB_SETTINGS)
        self.db.table   =  _TABLE['standby']
        self.rator      = Rator(self.db)

    def run(self, proxyList):
        logger.info('Running Validator.')
        self.rator.begin()
        while 1:
            try:
                if proxyList:
                    pen = len(proxyList)
                    logger.info('Proxies from Collector is detected,length : %d '%pen)
                    pop_len =  pen if pen <= VALIDATE_AMOUNT else VALIDATE_AMOUNT
                    stanby_proxies =[proxyList.pop() for x in range(pop_len)]
                    logger.info('Start to verify the collected proxy data,amount: %d '%pop_len)
                    gpool = pool.Pool(CONCURRENCY)
                    gevent.joinall([gpool.spawn(self.validate_proxy,i,self.rator) for i in stanby_proxies if i])
                time.sleep(VALIDATE_F)
            except Exception as e:
                logger.error('Error class : %s , msg : %s '%(e.__class__,e))
                self.rator.end()
                logger.info('Validator shuts down.')
                return

    def validate_proxy(self,proxy,rator=None,save=True):
        if not rator:
            raise Exception('No rator received.')
        if isinstance(proxy,dict):
            ip = proxy['ip']
            port = proxy['port']
        else:
            ip, port = proxy.split(':')
        proxies = {}
        session = requests.Session()
        session.mount('http://', HTTPAdapter(max_retries=VALIDATE_RETRY))
        session.mount('https://', HTTPAdapter(max_retries=VALIDATE_RETRY))
        try:
            response = session.get(proxy_validate_url.format(ip,port),
                                    proxies = proxies,
                                    headers=headers,
                                    timeout=10)
        except Exception as e:
            logger.error('Error class : %s , msg : %s ' % (e.__class__, e))
        else:
            data = response.json()
            res = data['msg'][0]
            if 'anony' in res and 'time' in res:
                bullet = {'ip':ip,'port':port,'anony_type':res['anony'],
                          'address':'','score':0,'valid_time':'',
                          'resp_time':res['time'],'test_count':0,
                          'fail_count':0,'createdTime':'','combo_success':1,'combo_fail':0,
                          'success_rate':'','stability':0.00}
                if save:
                    rator.mark_success(bullet)
                else:
                    proxy['anony_type']=res['anony']
                    proxy['resp_time'] = res['time']
                    rator.mark_update(proxy,collected=False)
            else:
                if not save:
                    rator.mark_fail(proxy)




