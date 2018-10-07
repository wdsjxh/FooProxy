#coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-05
"""
import logging
import time
import gevent
from gevent             import pool
from gevent             import monkey
from tools.util         import time_to_date
from tools.util         import get_ip_addr
from Helper.dbhelper    import Database
from DB.settings        import _DB_SETTINGS
from DB.settings        import _TABLE
from const.settings     import PRECISION
from config.config      import CONCURRENCY
from config.config      import MIN_SUCCESS_RATE
from config.config      import LOCAL_AMOUNT
from config.config      import VALIDATE_LOCAL

monkey.patch_socket()
logger = logging.getLogger('Rator')

class Rator(object):

    def __init__(self,db):
        self.raw_filter     = set()
        self.delete_filter  = set()
        self.local_data     = []
        self.db             = db

    def begin(self):
        self.db.table = _TABLE['standby']
        self.db.connect()
        self.pull_table(self.db.table)

    def end(self):
        self.db.close()

    def run(self,target):
        logger.info('Running Rator.')
        self.begin()
        while 1:
            try:
                if self.local_data:
                    pen = len(self.local_data)
                    logger.info('Imported the untested local proxies,length: %d '%pen)
                    pop_len = pen if pen <= LOCAL_AMOUNT else LOCAL_AMOUNT
                    logger.info('Start to verify the local proxy data,amount: %d ' % pop_len)
                    local_proxies = [self.local_data.pop() for i in range(pop_len)]
                    gpool = pool.Pool(CONCURRENCY)
                    gevent.joinall([gpool.spawn(target, i,self,False,self.db) for i in local_proxies if i])
                    time.sleep(VALIDATE_LOCAL)
                else:
                    self.local_data = self.import_db()
            except Exception as e:
                logger.error('Error class : %s , msg : %s ' % (e.__class__, e))
                self.end()
                logger.info('Rator shuts down.')
                raise e

    def import_db(self):
        data = self.db.all()
        if self.db.type == 'mysql':
            proxies = [':'.join([i[1],i[2]]) for i in data]
        elif self.db.type == 'mongodb':
            proxies = [':'.join([i['ip'],i['port']]) for i in data]
        else:
            logger.error('Illegal database backend :%s' % self.db.type)
            raise TypeError('Illegal database backend.')
        return proxies

    def pull_table(self,tname):
        if not tname:return
        table_data = self.db.all(tname)
        for i in table_data:
            if self.db.type == 'mongodb':
                self.raw_filter.add(':'.join([i['ip'],i['port']]))
            elif self.db.type == 'mysql':
                self.raw_filter.add(':'.join([i[1],i[2]]))
            else:
                logger.error('Illegal database backend :%s' % self.db.type)
                raise TypeError('Illegal database backend.')
        logger.info('Rator\'s raw filter initialized,length: %d '%len(self.raw_filter))

    def mark_success(self,data):
        ip = data['ip']
        port = data['port']
        proxy = ':'.join([ip,port])
        if proxy in self.raw_filter:
            logger.info('The proxy(%s) had been put into the local db,updating.'%proxy)
            self.mark_update(data)
            return
        address = get_ip_addr(ip)
        elapsed = round(int(data['resp_time'].replace('ms', '')) / 1000, 3)
        score = round(100 - 10 * (elapsed - 1), 2)
        stability = round(score/PRECISION,4)
        valid_time = time_to_date(int(time.time()))
        data['valid_time'] = valid_time
        data['address'] = address
        data['score'] = score
        data['test_count'] = 1
        data['stability'] = stability
        data['success_rate'] = str(round(1 - (data['fail_count'] / data['test_count']),
                                         3) * 100) + '%'
        self.db.save(data)
        self.raw_filter.add(proxy)

    def mark_fail(self,data,db=None):
        ip = data['ip']
        port = data['port']
        proxy = ':'.join([ip,port])
        update_data = {}
        _one_data = db.select({'ip': ip, 'port': port})
        if _one_data:
            _score = _one_data[5]
            _count = _one_data[8]
            _f_count = _one_data[9]
            _success_rate = _one_data[-2]
            _combo_fail = _one_data[-3]
            valid_time = time_to_date(int(time.time()))
            update_data['score'] = round(_score-5*((_f_count+1)/(_count+1))*(_combo_fail+1),2)
            update_data['combo_fail'] = _combo_fail+1
            update_data['combo_success'] = 0
            update_data['test_count'] = _count+1
            update_data['fail_count'] = _f_count+1
            update_data['valid_time'] = valid_time
            success_rate = round(1-(update_data['fail_count']/update_data['test_count']),3)
            update_data['success_rate'] = str(success_rate*100) + '%'
            update_data['stability'] = round(update_data['score']*update_data['test_count']*
                                             success_rate /PRECISION,4)
            if (_count >= 100 and _success_rate <= str(MIN_SUCCESS_RATE*100)+'%') or \
                    _score < 0:
                logger.warning('Deleting unstable proxy: %s '%proxy)
                try:
                    self.raw_filter.remove(proxy)
                except KeyError as e:
                    logger.error('Error class : %s , msg : %s ' % (e.__class__, e))
                db.delete({'ip':ip,'port':port})
                self.delete_filter.add(proxy)
            else:
                db.update({'ip':ip,'port':port},update_data)
                logger.info('Verify failed: %s '%proxy)

    def mark_update(self,data):
        db      = Database(_DB_SETTINGS)
        db.table = self.db.table
        db.connect()
        ip      = data['ip']
        port    = data['port']
        valid_time = time_to_date(int(time.time()))
        data['valid_time'] = valid_time
        elapsed = round(int(data['resp_time'].replace('ms', '')) / 1000, 3)
        score = round(100 - 10 * (elapsed - 1), 2)
        _one_data = db.select({'ip':ip,'port':port})
        if _one_data:
            _score = _one_data[5]
            _count = _one_data[8]
            _f_count = _one_data[9]
            _address = _one_data[4]
            _combo_success = _one_data[-4]
            _success_rate = round(float(_one_data[-2].replace('%',''))/100,4)
            score = round((score+_score*_count)/(_count+1)+0.5*(_combo_success+1)*_success_rate,2)
            address = get_ip_addr(ip) if _address=='unknown' else _address
            success_rate = round(1-(_f_count/(_count+1)),3)
            stability = round(score*(_count+1)*success_rate/PRECISION,4)
            data['address'] = address
            data['score'] = score
            data['test_count'] = _count+1
            data['combo_success'] = _combo_success+1
            data['success_rate'] = str(success_rate*100)+'%'
            data['stability'] = stability
            del data['fail_count']
            db.update({'ip':ip,'port':port},data)
            db.close()


