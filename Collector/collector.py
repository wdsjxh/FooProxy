#coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""
import time
from tools.threads import CrawlThread
from Collector.crawlers import builtin_crawlers
from custom.custom import  my_crawlers
from inspect    import isfunction
from config       import COLLECT_TIME_GAP

class Collector(object):
    def __init__(self):
        self.__proxyList = None
        self.__crawlers  = my_crawlers


    def find_crawlers(self):
        _crawlers = [i for i in builtin_crawlers if isfunction(i)]
        custom_crawlers  = [i for i in self.__crawlers if isfunction(i)]
        _crawlers.extend(custom_crawlers)
        return _crawlers


    def run(self,proxyList):
        while 1:
            results = []
            t_res   = set()
            self.__proxyList = proxyList
            funcs = self.find_crawlers()
            threads = [CrawlThread(i) for i in funcs]
            for i in threads:
                i.start()
            for i in threads:
                i.join()
                results.append(i.get_result())
            for res in results:
                for x in res:
                    t_res.add(x)
            self.__proxyList.extend(t_res)
            time.sleep(COLLECT_TIME_GAP)
