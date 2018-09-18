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
import jsoncd 

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

# models.py
class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Numeric(4), primary_key=True)
    test_name = db.Column(db.String(20), nullable=False)
    def __init__(self, test_name):
        self.test_name = test_name
    def __repr__(self):
        return '<Test %r>' % self.test_name

# manage.py
from flask_script import Manager, Server

manager = Manager(app) # 設置你的 app
manager.add_command('runserver', Server()) # 設置 python manage.py runserver 為啟動 server 指令

# 設置 python manage.py shell 為啟動交互式指令 shell 的指令
@manager.shell
def make_shell_context():
 return dict(app=app, Test=Test)

if __name__ == '__main__':
 manager.run()
