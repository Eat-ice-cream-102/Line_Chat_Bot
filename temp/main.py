'''
pip install --upgrade pip
pip install flask==0.12
pip install flask-sqlalchemy
pip install pymysql
'''
# main.py
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import pymysql
import json

app = Flask(__name__)

secretMysqlFileContentJson=json.load(open("./mysql_key", 'r'))
HOST = secretMysqlFileContentJson.get('Host')
USER = secretMysqlFileContentJson.get("User")
PASSWD = secretMysqlFileContentJson.get("Passwd")
DB = secretMysqlFileContentJson.get("DB")
CHARTSET = "utf8"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{user}:{password}@{host}:3306/{dbname}?charset={charset}'.format(user=USER, password=PASSWD, host=HOST, dbname=DB, charset=CHARTSET)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
