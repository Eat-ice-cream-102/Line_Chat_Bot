# CONFIG ##########################################
# PACKAGES
## Flask
from flask import Flask, request, abort
## Line
from linebot import ( LineBotApi, WebhookHandler )
from linebot.exceptions import ( InvalidSignatureError, LineBotApiError )
from linebot.models import ( MessageEvent, PostbackEvent, TextMessage, TextSendMessage, FollowEvent )
## MySQL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import pymysql
## else
import json, requests

# APP.CONSTANTS
## Line
line_key=json.load(open("./requirements/line_key", 'r'))
CHANNEL_ACCESS_TOKEN = line_key.get("Channel_access_token")
CHANNEL_SECRET = line_key.get("Channel_secret")
MY_USER_ID = line_key.get("My_user_ID")
RICH_MENU_ID = line_key.get("Rich_menu_ID")
CHANNEL_ID = line_key.get("Channel_ID")
SERVER_URL = line_key.get("Server_URL")

## MySQL
mysql_key=json.load(open("./requirements/mysql_key", 'r'))
HOST = mysql_key.get('Host')
USER = mysql_key.get("User")
PASSWD = mysql_key.get("Passwd")
DB = mysql_key.get("DB")
CHARTSET = "utf8"


# APP.INSTANCE
app = Flask(__name__, instance_relative_config=True)
app.config['DEBUG'] = None


# LINE CONNECT
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# MySQL CONNECT
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{user}:{password}@{host}:3306/{dbname}?charset={charset}'.format(user=USER, password=PASSWD, host=HOST, dbname=DB, charset=CHARTSET)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USER}:{PASSWD}@{HOST}:3306/{DB}?charset={CHARTSET}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# APP ###########################################
# MODELS
class employee(db.Model):
    __tablename__ = 'employee'
    test_no = db.Column(db.Numeric(10), primary_key=True)
    line_id = db.Column(db.Numeric(40)),
    test_name = db.Column(db.String(20), nullable=False)
    def __init__(self, test_no, test_name):
        self.test_no = test_no
        self.test_name = test_name
    def __repr__(self):
        return '%s,%s,%s' % (self.test_no, self.line_id, self.test_name)

class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Numeric(4), primary_key=True)
    test_name = db.Column(db.String(20), nullable=False)
    def __init__(self, id, test_name):
        self.id = id
        self.test_name = test_name
    def __repr__(self):
        return '<Test %r>' % self.test_name


# ROUTE
## route/
@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(FollowEvent) # message=None
def get_profile(event):
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
        user_id = profile.user_id
        display_name = profile.display_name
        picture_url = profile.picture_url
        status_message = profile.status_message
        judge = employee.query.filter(employee.line_id == user_id)
    except LineBotApiError as e:
        app.logger.exception(e)
    # 如果對的到user_id的資訊，就代表是被unfollow又再回來
    if judge.one_or_none() == None:
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text="歡迎加入吃冰大家族！，請輸入註冊name以進行綁定"))

        @handler.add(MessageEvent, message=TextMessage)
        def handle_message(event):
            sign_name = event.message.text
            if
        employee.query.filter(employee.test_name == ).update({'employee.line_id':user_id})
        db.session.commit()
    # 如果對不到user_id的資訊，就代表是新會員（進行資料庫寫入）
    else:
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text="T^T...親，你終於回來了！我想您想的好苦啊！！！"))


    #linkMenuEndpoint = 'https://api.line.me/v2/bot/user/%s/richmenu/%s' % (user_id, RICH_MENU_ID)  # 設定 request address
    linkMenuEndpoint = f'https://api.line.me/v2/bot/user/{user_id}/richmenu/{RICH_MENU_ID}'
    #linkMenuRequestHeader = {'Content-Type':'image/png','Authorization':'Bearer %s' % CHANNEL_ACCESS_TOKEN} # 設定 headers
    linkMenuRequestHeader = {'Content-Type':'image/png','Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'}
    lineLinkMenuResponse = requests.post(linkMenuEndpoint,headers=linkMenuRequestHeader) # check Response

@handler.add(PostbackEvent)
def handle_post_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    if event.postback.data.find('orderHistory')== 0:
        line_bot_api.reply_message(event.reply_token, 
            TextMessage(text="Here's your Last Order"))
    elif event.postback.data.find('myCoupon')== 0:
        # take data
        line_bot_api.reply_message(event.reply_token, 
            TextMessage(text="Oh! Empty!"))
    elif event.postback.data.find('customerService')== 0:
        line_bot_api.reply_message(event.reply_token,
            TextMessage(text="Please type your suggest below. Any Command is welcome."))
#        @handler.add(MessageEvent, message=TextMessage)
#        def handle_message(event):
#            while True: 
#                if event.message.text != "客服專區":
#                    with open("./customerComplain.txt", "a") as f:
#                        f.write(event.message.text)
#                    line_bot_api.reply_message(event.reply_token,
#                        TextMessage(text="Thank you, We will reply you ASAP."))
#                    break
