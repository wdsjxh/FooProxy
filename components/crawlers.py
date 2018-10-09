# coding:utf-8
"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""
import re
import logging
import requests
from tools.util         import base64_decode
from tools.util         import get_cookies
from tools.util         import get_nyloner_params
from const.settings     import headers
from const.settings     import _66ip_params
from const.settings     import builtin_crawl_urls   as _urls
from bs4                import BeautifulSoup        as bs

logger = logging.getLogger('Collector')

def nyloner():
    s       = requests.Session()
    url     = _urls['nyloner']['url']
    count   = _urls['nyloner']['count']
    params  = get_nyloner_params(1,count)
    try:
        cookies = get_cookies(url, headers=headers)
        __cookie = {'sessionid': cookies['sessionid']}
        response = s.get(url,headers=headers,params=params,cookies=__cookie)
    except Exception as e:
        logger.error('Error class : %s , msg : %s ' % (e.__class__, e))
    else:
        crypted_data = response.json()
        data = base64_decode(crypted_data['list'])
        res = [':'.join([i['ip'],i['port']]) for i in data]
        return res

def ip66():
    s       = requests.Session()
    url     = _urls['66ip']['url']
    try:
        response = s.get(url,headers=headers,params=_66ip_params)
        soup = bs(response.text, 'lxml')
    except Exception as e:
        logger.error('Error class : %s , msg : %s ' % (e.__class__, e))
    else:
        data = [re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b\:\d+', i)
                for i in soup.body.text.split('\r\n') if i.strip()]
        data = [i[0] for i in data if i]
        return data


builtin_crawlers = [nyloner,ip66,]