#coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""

import logging
from APIserver.apiserver    import app
from components.collector   import Collector
from components.validator   import Validator
from components.detector    import Detector
from components.rator       import Rator
from components.dbhelper    import Database
from components.scanner     import Scaner
from multiprocessing        import Pool
from multiprocessing        import Manager
from config.DBsettings      import _DB_SETTINGS
from config.config          import MODE
from const.settings         import RUN_FUNC

logger = logging.getLogger()

class Workstation(object):
    def __init__(self):
        self.collector = Collector()
        self.validator = Validator()
        self.detector  = Detector()
        self.scanner   = Scaner()
        self.proxyList = Manager().list()

    def run_validator(self,proxyList):
        self.validator.run(proxyList)

    def run_collector(self,proxyList):
        self.collector.run(proxyList)

    def run_detector(self,*params):
        self.detector.run()

    def run_scanner(self,*params):
        self.scanner.run()

    def work(self):
        pool = Pool(5)
        func = []
        for i in MODE:
            if MODE[i]:
                func.append(eval('self.'+RUN_FUNC[i]))
        [pool.apply_async(fun,args=(self.proxyList,)) for fun in func]
        pool.close()
        logger.info('Workstation process pool starting.....OK')
        app.run()



