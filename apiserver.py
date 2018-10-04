# coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'hello'



