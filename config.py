# PACKAGES
## Flask
from flask import Flask, request, abort
## Line
from linebot import ( LineBotApi, WebhookHandler )
from linebot.exceptions import ( InvalidSignatureError )
from linebot.models import ( MessageEvent, TextMessage, TextSendMessage, FollowEvent )
## MySQL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import pymysql
## else
import json

# APP.CONSTANTS
## Line
line_key=json.load(open("./requirements/line_key", 'r'))
CHANNEL_ACCESS_TOKEN = line_key.get("Channel_access_token")
CHANNEL_SECRET = line_key.get("Channel_secret")
MY_USER_ID = line_key.get("My_user_ID")
RICH_MENU_ID = line_key.get("Rich_menu_ID")
''' yet to be used
CHANNEL_ID = line_key.get("Channel_ID")
SERVER_URL = line_key.get("Server_URL")
'''
## MySQL
mysql_key=json.load(open("./requirements/mysql_key", 'r'))
HOST = mysql_key.get('Host')
USER = mysql_key.get("User")
PASSWD = mysql_key.get("Passwd")
DB = mysql_key.get("DB")
CHARTSET = "utf8"


# APP.INSTANCE
app = Flask(__name__)


# LINE CONNECT
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# MySQL CONNECT
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{user}:{password}@{host}:3306/{dbname}?charset={charset}'.format(user=USER, password=PASSWD, host=HOST, dbname=DB, charset=CHARTSET)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
