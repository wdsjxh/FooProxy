#coding:utf-8
"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""
import time
import json
import base64
import hashlib
import requests
from const.settings import IP_check_url
from const.settings import headers
from bs4 import BeautifulSoup as bs

def time_to_date(timestamp):
    """
    时间戳转换为日期
    :param timestamp : 时间戳，int类型，如：1537535021
    :return:转换结果日期，格式： 年-月-日 时:分:秒
    """
    timearr = time.localtime(timestamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timearr)
    return  otherStyleTime

def get_ip_addr(ip):
    """
    获取ip的地址信息
    :param ip : IP地址
    :return: 地址信息
    """
    try:
        resp = requests.get(IP_check_url+ip,headers=headers)
        rep = bs(resp.text,'lxml')
        try:
            res = rep('code')[1].text
        except Exception as e:
            return 'unknown'
        return res
    except Exception as e:
        return 'unknown'


def get_cookies(url, headers=headers, params={},proxies={}):
    """
    异步获取某个url的cookie并返回
    :param url: 要获取cookie的网址
    :param headers: 给定的请求头部
    :param params: 请求参数
    :return: 需要的cookies
    """
    cookies = requests.get(url, headers=headers, params=params,proxies=proxies).cookies
    return cookies

def get_nyloner_params(page,num):
    """
    获取代理ip提供网站:https://www.nyloner.cn的请求伪造参数
    :param page: 请求页面所在页数 (一般设为1，后续num设定爬取多少条ip便可)
    :param num: 这一页要爬取的代理ip条数
    :return: 有效的请求伪造参数
    """
    timestamp = int(time.time())
    token = hashlib.md5(str(page).encode(encoding='UTF-8')+
                        str(num).encode(encoding='UTF-8')+
                        str(timestamp).encode(encoding='UTF-8')).hexdigest()
    return {
        'page':page,
        'num':num,
        'token':token,
        't'	: timestamp,
    }

def base64_decode(data,key='\x6e\x79\x6c\x6f\x6e\x65\x72'):
    """
    IP代理网站：https://www.nyloner.cn/proxy的代理抓取json数据解密函数
    :param data: 抓取的json数据的list的加密内容
    :param key : 加密的key 默认为'\x6e\x79\x6c\x6f\x6e\x65\x72'即是'nyloner'
    :return: 返回解密list内容,json格式
    """
    data = base64.b64decode(data)
    code = ''
    for x in range(len(data)):
        j = x % len(key)
        code += chr((data[x]^ord(key[j]))%256)
    decoded_data = str(base64.b64decode(code)).lstrip('b').strip('\'')
    return json.loads(decoded_data)