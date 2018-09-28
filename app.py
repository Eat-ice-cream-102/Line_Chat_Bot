# CONFIG ##########################################
# PACKAGES
## Flask
from flask import Flask, request, abort
## Line
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError, LineBotApiError)
from linebot.models import *
## MySQL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import pymysql
## else
import json, time, datetime, re, requests

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
#record in_out
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
        return '%s,%s,%s' % (self.phone, self.in_out, self.test_no)

class survey (db.Model):
    __tablename__ = 'survey'
    survey_no = db.Column(db.Integer, primary_key=True)
    test_no = db.Column(db.Numeric(10), db.ForeignKey('test.test_no'), nullable=False)
    time = db.Column(db.DateTime)
    satisfaction = db.Column(db.Numeric(1))
    def __init__(self, test_no, time=datetime.datetime.now()):
        self.test_no = test_no
        self.time = time
    def __repr__(self):
        return '%s' % (self.satisfaction)

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

'''FAILED SECTION
recommendEndpoint = "https://api.line.me/v2/bot/message/push"
recommendHeaders = {'Content-Type': 'application/json', 'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'}
loadRecommendJson = json.load(open("./static/message/recommend", 'r'))  # set recommend-list
recommendData = {"to": line, "messages": [loadRecommendJson]}
recommend_response = requests.post(recommendEndpoint, headers=recommendHeaders, data=recommendData)
'''
UNRECOMMENDED_STATUS = test.query.filter(test.in_out != 2)
OUT_STATUS = 0
IN_STATUS = 1
RECOMMEND_FINISHED = 2
# check if any non-recommend issue
while True:
    if UNRECOMMENDED_STATUS.one_or_none():
        # is it possibile below first() represent two different user_id??
        phone = UNRECOMMENDED_STATUS.first().phone
        status = UNRECOMMENDED_STATUS.first().in_out
        test_no = UNRECOMMENDED_STATUS.first().test_no
        line = employee.query.filter(employee.phone == phone).one().line
        # make sure we have buyer's line_id
        if line != None:
            # in situation
            if status == IN_STATUS:
                # push best-seller items
                columns = []
                for i in range(0,9,1):
                    uriAction = URIAction(lable, uri='')
                    carouselColumn = CarouselColumn(thumbnail_image_url, text, actions=[uriAction])
                    columns.append(carouselColumn)
                bestSell_templateMessage = TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(columns)
                )
                line_bot_api.push_message(line, bestSell_templateMessage)
                test.query.filter(test.test_no == test_no).update({"in_out" : RECOMMEND_FINISHED})
                db.session.commit()
            # out situation
            elif status == OUT_STATUS:
                # push recommendTemplate
                columns = []
                for i in range(0,9,1):
                    uriAction = URIAction(lable, uri='')
                    carouselColumn = CarouselColumn(thumbnail_image_url, text, actions=[uriAction])
                    columns.append(carouselColumn)
                recommend_templateMessage = TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(columns)
                )
                line_bot_api.push_message(line, recommend_templateMessage)

                # create survey data
                addSurvey = survey(test_no)
                db.session.add(addSurvey)
                # push surveyTemplate
                survey_templateMessage = TemplateSendMessage(
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        thumbnail_image_url='https://epaper.land.gov.taipei/File/Get/93250086-fe2f-45c8-81e1-35a8c7836d6b',
                        text='感謝您的光臨，請問對於今日整體購物體驗滿意嗎??',
                        actions=[
                            PostbackAction(
                                label='非常滿意',
                                text='非常滿意',
                                data='[survey]4,%s'%test_no
                            ),
                            PostbackAction(
                                label='滿意',
                                text='滿意',
                                data='[survey]3,%s'%test_no
                            ),
                            PostbackAction(
                                label='不滿意',
                                text='不滿意',
                                data='[survey]2,%s'%test_no
                            ),
                            PostbackAction(
                                label='非常不滿意',
                                text='非常不滿意',
                                data='[survey]1,%s'%test_no
                            )
                        ]
                    )
                )
                line_bot_api.push_message(line, survey_templateMessage)
                # update status
                test.query.filter(test.test_no == test_no).update({"in_out" : RECOMMEND_FINISHED})
                db.session.commit()
        else:
            continue
    else:
        time.sleep(10)

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
    # fill in cellphone number to connect line account
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
    # rich_menu function
    if event.postback.data.find('[menu]') == 0:
        if event.postback.data[5:] == 'location':
            line_bot_api.reply_message(event.reply_token, LocationSendMessage(title='吃冰', address='320桃園市中壢區中大路300號', latitude=24.967798, longitude=121.191802))
        elif event.postback.data[5:] == 'web':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='https://google.com.tw'))
        elif event.postback.data[5:] == 'custimerService':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Any comment is welcome.'))
    # survey function
    elif event.postback.data.find('[survey]') == 0:
        test_no = re.match('[survey](\d),(\d+)', event.postback.data).group(1)
        satisfaction = re.match('[survey](\d),(\d+)', event.postback.data).group(2)
        survey.query.filter(survey.test_no == test_no).update({'satisfaction': satisfaction})
        db.session.commit()
        if satisfaction < 3:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="We are sorry to cause your unpleasent, if you need our service member to contact you?"))