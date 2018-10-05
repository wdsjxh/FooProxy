#coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""

import threading

class CrawlThread(threading.Thread):
    def __init__(self, func, args=() ):
        super(CrawlThread, self).__init__()
        self.func = func
        self.args = args
        self.setDaemon(True)

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            return None


class ValidateStandbyThread(threading.Thread):
    def __init__(self, func, args=() ):
        super(ValidateStandbyThread, self).__init__()
        self.func = func
        self.args = args
        self.setDaemon(True)

    def run(self):
        self.result = self.func(*self.args)