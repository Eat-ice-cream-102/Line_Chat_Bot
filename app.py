# CONFIG ##########################################
# PACKAGES
## Flask
from flask import Flask, request, abort
## Line
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError, LineBotApiError)
from linebot.models import (TemplateSendMessage, CarouselTemplate, MessageEvent, PostbackEvent, TextMessage, TextSendMessage, FollowEvent)
## MySQL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import pymysql
## else
import json, requests, time

# APP.CONSTANTS
## Line
line_key = json.load(open("./requirements/line_key", 'r'))
CHANNEL_ACCESS_TOKEN = line_key.get("Channel_access_token")
CHANNEL_SECRET = line_key.get("Channel_secret")
MY_USER_ID = line_key.get("My_user_ID")
RICH_MENU_ID = line_key.get("Rich_menu_ID")
CHANNEL_ID = line_key.get("Channel_ID")
SERVER_URL = line_key.get("Server_URL")
## MySQL
mysql_key = json.load(open("./requirements/mysql_key", 'r'))
HOST = mysql_key.get('Host')
USER = mysql_key.get("User")
PASSWD = mysql_key.get("Passwd")
DB = mysql_key.get("DB")
CHARTSET = "utf8"

# APP.INSTANCE
app = Flask(__name__, instance_relative_config=True, static_url_path='/static')
app.config['DEBUG'] = None

# CONNECTION
## LINE CONNECT
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
## MySQL CONNECT
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USER}:{PASSWD}@{HOST}:3306/{DB}?charset={CHARTSET}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# APP ###########################################
# MODELS
class employee(db.Model):
    __tablename__ = 'employee'
    phone = db.Column(db.String(10), primary_key=True)
    line = db.Column(db.String(40))
    test_name = db.Column(db.String(20), nullable=False)
    def __init__(self, phone, line, test_name):
        self.phone = phone
        self.line = line
        self.test_name = test_name
    def __repr__(self):
        return '%s' % self.line

class test(db.Model):
    __tablename__ = 'test'
    test_no = db.Column(db.Numeric(10), primary_key=True)
    phone = db.Column(db.String(10),db.ForeignKey('employee.phone'), nullable=False)
    in_out = db.Column(db.Numeric(1))
    def __init__(self, test_no, phone, in_out):
        self.test_no = test_no
        self.phone = phone
        self.in_out = in_out
    def __repr__(self):
        return '%s,%s,%s' % (self.phone, self.in_out, test_no)

class survey (db.Model):
    __tablename__ = 'survey'
    __table_args__ = (db.PrimaryKeyConstraint('line', 'survey_no'))
    survey_no = db.Column(db.Numeric(10), nullable=False)
    line = db.Column(db.String(40), nullable=False)
    time = db.Column(db.datetime.datetime(10))
    satisfaction = db.Column(db.Numeric(1))
    command = db.Column(db.String(50))
    def __init__(self, line, satisfaction, time=datetime.datetime.now()):
        self.line = line
        self.satisfaction = satisfaction
        self.time = time
    def __repr__(self):
        return '%s,%s' % (self.survey_no, self.satisfaction)

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

def recommend():
    UNRECOMMENDED_STATUS = test.query.filter(test.in_out != 2)
    OUT_STATUS = 0
    IN_STATUS = 1
    # check if any non-recommend issue
    while UNRECOMMENDED_STATUS.one_or_none():
        # is it possibile below first() represent two different user_id??
        phone = UNRECOMMENDED_STATUS.first().split(',')[0]
        status = UNRECOMMENDED_STATUS.first().split(',')[1]
        test_no = UNRECOMMENDED_STATUS.first().split(',')[2]
        user_id = employee.query.filter(employee.phone == phone)
        # make sure we have buyer's line_id
        if user_id != None:
            # in situation
            if status == IN_STATUS:
                # push best-seller items
                recommendEndpoint = "http://api.line.me/v2/bot/message/push"
                recommendHeaders = {"Content-Type": "application/json", "Authorization": f'"Bearer {CHANNEL_ACCESS_TOKEN}"'}
                uploadRecommendJson = json.load(open("./requirements/recommend", 'r'))  # set recommend-list
                recommendData = {"to": user_id, "messages": uploadRecommendJson}
                recommend_response = requests.post(recommendEndpoint, headers=recommendHeaders, data=recommendData)
            # out situation
            elif status == OUT_STATUS:
                # push items according to bought-list
                recommendEndpoint = "http://api.line.me/v2/bot/message/push"
                recommendHeaders = {"Content-Type": "application/json", "Authorization": f'"Bearer {CHANNEL_ACCESS_TOKEN}"'}
                uploadRecommendJson = json.load(open("./requirements/recommend", 'r'))  # set recommend-list
                recommendData = {"to": user_id, "messages": uploadRecommendJson}
                recommend_response = requests.post(recommendEndpoint, headers=recommendHeaders, data=recommendData)
                surveyJson = json.load(open("./requirements/survey", 'r'))
                surveyData = {"to": user_id, "messages": surveyJson}
                recommend_response = requests.post(recommendEndpoint, headers=recommendHeaders, data=surveyData)
        else:
            time.sleep(10)
            break

@handler.add(FollowEvent)
def handle_follow_event(event):
    try:
        # 會員綁定賴帳戶檢查
        user_id = event.source.user_id
        judge_id = employee.query.filter(employee.line == user_id)
        # 如果對不到user_id的資訊，就代表是新會員（進行資料庫寫入）
        if judge_id.one_or_none() == None:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text="歡迎加入吃冰大家族！，請輸入註冊phone number以進行綁定"))
        # 如果對的到user_id的資訊，就代表是被unfollow又再回來
        else:
            line_bot_api.reply_message(event.reply_token,
                                       TextSendMessage(text="T^T...親，你終於回來了！我想您想的好苦啊！！！"))
        # 綁定菜單至使用者
        linkMenuEndpoint = f'https://api.line.me/v2/bot/user/{user_id}/richmenu/{RICH_MENU_ID}'  # 設定 request address
        linkMenuRequestHeader = {'Content-Type': 'image/png', 'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'}  # 設定 headers
        lineLinkMenuResponse = requests.post(linkMenuEndpoint, headers=linkMenuRequestHeader)  # check Response
    except LineBotApiError as e:
        app.logger.exception(e)

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if re.match('(09\d{8})', event.message.text).groups():
        user_id = event.source.user_id
        sign_data = event.message.text
        connection = employee.query.filter(employee.phone == sign_data)
        if connection.one_or_none() != None:
            employee.query.filter(employee.phone == sign_data).update({'line': user_id})
            db.session.commit()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Connect Successfully."))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Not Found, Please Try Again."))
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))

@handler.add(PostbackEvent)
def handle_post_message(event):
    if event.postback.data.find('[menu]') == 0:
        line_bot_api.reply_message(event.reply_token, TextMessage(text="Here's your Last Order"))
    elif event.postback.data.find('[survey]') == 0:
        satisfaction = event.postback.data[7:]
        addOne = survey(event.source.user_id,satisfaction)
        db.session.add(addOne)
        db.session.commit()
        if satisfaction < 3:
            line_bot_api.reply_message(event.reply_token, TextMessage(text="Here's your Last Order"))


