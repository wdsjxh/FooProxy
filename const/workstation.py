#coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""

from APIserver.apiserver    import app
from Collector.collector    import Collector
from Validator.validator    import Validator
from Detector.detector      import Detector
from Rator.rator            import Rator
from Helper.dbhelper        import Database
from multiprocessing        import Pool
from multiprocessing        import Manager
from DB.settings            import _DB_SETTINGS
from DB.settings            import _TABLE

class Workstation(object):

    def __init__(self):
        self.collector = Collector()
        self.validator = Validator()
        self.detector  = Detector()
        self.database  = Database(_DB_SETTINGS)
        self.proxyList = Manager().list()
        self.rator     = Rator(self.database)

    def preparing(self):
        self.database.make_preparation(_TABLE.values())

    def run_validator(self,proxyList):
        self.validator.run(proxyList)

    def run_collector(self,proxyList):
        self.collector.run(proxyList)

    def run_detector(self,*params):
        self.detector.run()

    def run_rator(self,*params):
        self.rator.run(self.validator.validate_proxy)

    def work(self):
        self.preparing()
        pool = Pool(4)
        func = [self.run_detector,self.run_rator]
        results = [pool.apply_async(fun,args=(self.proxyList,)) for fun in func]
        pool.close()
        app.run()



