# coding:utf-8

"""
    @author  : linkin
    @email   : yooleak@outlook.com
    @date    : 2018-10-04
"""
import json
from flask import Flask

from components.dbhelper import Database
from config.DBsettings import _TABLE,_DB_SETTINGS


app = Flask(__name__)
db  = Database(_DB_SETTINGS)
db.table = _TABLE['standby']
db.connect()


@app.route('/')
def index():
    return 'hello'


@app.route('/proxy')
@app.route('/proxy/<string:kind>')
@app.route('/proxy/<string:kind>/<int:num>')
def get_proxy(kind='anony',num=1):
    data = db.select({'ip':'119.27.177.169','port':'80'})[1:]
    return json.dumps(data)


