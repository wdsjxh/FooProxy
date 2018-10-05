#coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-05
"""

import time
from tools.BloomFilter  import BloomFilter
from config.config      import MAX_AMOUNT
from config.config      import ERROR_RATE
from tools.util         import time_to_date
from tools.util         import get_ip_addr
class Rator(object):

    def __init__(self,db):
        self.raw_filter     = BloomFilter(ERROR_RATE,MAX_AMOUNT)
        self.delete_filter  = BloomFilter(ERROR_RATE,MAX_AMOUNT)
        self.db             = db

    def begin(self):
        self.db.connect()
        self.pull_table(self.db.table)

    def end(self):
        self.db.close()

    def pull_table(self,tname):
        if not tname:return
        table_data = self.db.all(tname)
        for i in table_data:
            self.raw_filter.insert(':'.join([i[1],i[2]]))

    def mark_success(self,data):
        ip = data['ip']
        port = data['port']
        valid_time = time_to_date(int(time.time()))
        proxy = ':'.join([ip,port])
        if self.raw_filter.is_exists(proxy):
            if not self.delete_filter.is_exists(proxy):
                self.mark_update(data)
                return
        address = get_ip_addr(ip)
        elapsed = round(int(data['resp_time'].replace('ms', '')) / 1000, 3)
        score = str(round(100 - 10 * (elapsed - 1),2))
        data['valid_time'] = valid_time
        data['address'] = address
        data['score'] = score
        data['test_count']=1
        data['success_rate'] =str(round(1-(data['fail_count']/data['test_count']),3)*100)+'%'
        self.db.save(data)



    def mark_fail(self,data):
        pass

    def mark_update(self,data):
        pass

