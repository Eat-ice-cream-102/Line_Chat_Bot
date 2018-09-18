from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import pymysql
import json

app = Flask(__name__)

# 常數設定
secretMysqlFileContentJson=json.load(open("./mysql_key", 'r'))
HOST = secretMysqlFileContentJson.get('Host')
USER = secretMysqlFileContentJson.get("User")
PASSWD = secretMysqlFileContentJson.get("Passwd")
DB = secretMysqlFileContentJson.get("DB")
CHARTSET = "utf8"

# 建立DB連線
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{user}:{password}@{host}:3306/{dbname}?charset={charset}'.format(user=USER, password=PASSWD, host=HOST, dbname=DB, charset=CHARTSET)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # 追蹤物件的修改並且傳送訊號。
app.config['SQLALCHEMY_ECHO'] = True # 記錄所有發到標準輸出(stderr)的語句，利於除錯
db = SQLAlchemy(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
