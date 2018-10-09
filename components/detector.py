# coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-07
"""
import time
import asyncio
import logging
from gevent                 import monkey
from components.dbhelper    import Database
from config.DBsettings      import _DB_SETTINGS
from config.DBsettings      import _TABLE
from config.config          import DETECT_HIGH_AMOUNT
from config.config          import DETECT_LOCAL
from config.config          import DETECT_AMOUNT
from config.config          import STABLE_MIN_RATE
from config.config          import STABLE_MIN_COUNT
from config.config          import DELETE_COMBO

monkey.patch_socket()
logger = logging.getLogger('Detector')

class Detector(object):
    def __init__(self):
        self.standbyDB  = Database(_DB_SETTINGS)
        self.stableDB   = Database(_DB_SETTINGS)
        self.standbyDB.table  = _TABLE['standby']
        self.stableDB.table   = _TABLE['stable']
        self.standby_data     = []
        self.stable_data      = []

    def begin(self):
        self.stableDB.connect()
        self.standbyDB.connect()

    def end(self):
        self.standbyDB.close()
        self.stableDB.close()

    def run(self):
        logger.info('Running Detector.')
        self.begin()
        loop = asyncio.get_event_loop()
        while 1:
            try:
                self.detect_standby(loop)
                self.detect_stable(loop)
                time.sleep(DETECT_LOCAL)
            except Exception as e:
                logger.error('Error class : %s , msg : %s ' % (e.__class__, e))
                self.end()
                loop.close()
                logger.info('Detector shuts down.')
                return

    def detect_standby(self,loop):
        if self.standby_data:
            pen = len(self.standby_data)
            logger.info('Imported the "standby" database\' data,length: %d ' % pen)
            pop_len = pen if pen <= DETECT_AMOUNT else DETECT_AMOUNT
            logger.info('Start to detect the local valid data,amount: %d ' % pop_len)
            standby_data = [self.standby_data.pop() for i in range(pop_len)]
            tasks = [self._detect_standby(i) for i in standby_data]
            loop.run_until_complete(asyncio.gather(*tasks))
            logger.info('Detection finished.Left standby data length:%d' % len(self.standby_data))
        else:
            self.standby_data = self.standbyDB.all()

    def detect_stable(self,loop):
        if self.stable_data:
            pen = len(self.stable_data)
            logger.info('Imported the "stable" database\' data,length: %d ' % pen)
            pop_len = pen if pen <= DETECT_HIGH_AMOUNT else DETECT_HIGH_AMOUNT
            logger.info('Start to detect the high scored data,amount: %d ' % pop_len)
            stable_data = [self.stable_data.pop() for i in range(pop_len)]
            tasks = [self._detect_stable(i) for i in stable_data]
            loop.run_until_complete(asyncio.gather(*tasks))
            logger.info('Detection finished.Left stable data length:%d' % len(self.stable_data))
        else:
            self.stable_data = self.stableDB.all()

    async def _detect_standby(self,data):
        del data['_id']
        ip = data['ip']
        port = data['port']
        proxy = ':'.join([ip,port])
        if data['test_count']<STABLE_MIN_COUNT or round(float(data['success_rate'].replace('%',''))/100,4) < STABLE_MIN_RATE:
            return
        condition = {'ip':ip,'port':port}
        _one_data = self.stableDB.select(condition)
        if _one_data:
            self.stableDB.update(condition,data)
        else:
            self.stableDB.save(data)
            logger.info('Find a stable proxy: %s , put it into the stable database.' % proxy)

    async def _detect_stable(self,data):
        del data['_id']
        ip = data['ip']
        port = data['port']
        proxy = ':'.join([ip,port])
        condition = {'ip':ip,'port':port}
        res = self.standbyDB.select(condition)
        _one_data = res[0] if res else None
        if not bool(_one_data):
            self.stableDB.delete(condition)
            logger.warning(
                'The high scored proxy: %s had been deleted from the standby database.It\'s unavailable.' % proxy)
        else:
            if round(float(_one_data['success_rate'].replace('%',''))/100,4) < STABLE_MIN_RATE or _one_data['combo_fail'] >= DELETE_COMBO:
                self.stableDB.delete(condition)
                logger.warning(
                    'The high scored proxy: %s is not that stable now.It\'s Removed.' % proxy)
            else:
                del _one_data['_id']
                self.stableDB.update(condition,data)

