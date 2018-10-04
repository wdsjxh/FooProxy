#coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""
from apiserver  import app
from collector  import Collector
from validator  import Validator
from detector   import Detector
from multiprocessing import Pool
from multiprocessing import Manager

class Workstation(object):

    def __init__(self):
        self.collector = Collector()
        self.validator = Validator()
        self.detector  = Detector()
        self.proxyList = Manager().list()

    def run_validator(self,proxyList):
        self.validator.run(proxyList)

    def run_collector(self,proxyList):
        self.collector.run(proxyList)

    def run_detector(self,*params):
        self.detector.run()

    def work(self):
        pool = Pool(4)
        func = [self.run_collector,self.run_validator,self.run_detector]
        results = [pool.apply_async(fun,args=(self.proxyList,)) for fun in func]
        pool.close()
        app.run()



