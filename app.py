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
## else
import json, time, re, requests

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

# Models ##########################################
class customer(db.Model):
    __tablename__ = 'customer'
    phone = db.Column(db.String(10), primary_key=True)
    line = db.Column(db.String(40))
    customerName = db.Column(db.String(20), nullable=False)
    def __init__(self, phone, line, test_name):
        self.phone = phone
        self.line = line
        self.test_name = test_name
    def __repr__(self):
        return '%s,%s' % (self.line, self.test_name)

class inOutRecord(db.Model):
    __tablename__ = 'inOutRecord'
    come_time = db.Column(db.DateTime, primary_key=True)
    phone = db.Column(db.String(10),db.ForeignKey('customer.phone'), nullable=False)
    in_out = db.Column(db.Numeric(1))
    def __init__(self, come_time, phone, in_out):
        self.come_time = come_time
        self.phone = phone
        self.in_out = in_out
    def __repr__(self):
        return '%s,%s' % (self.phone, self.in_out)

class survey (db.Model):
    __tablename__ = 'survey'
    survey_no = db.Column(db.Integer, primary_key=True, nullable=False)
    come_time = db.Column(db.DateTime, db.ForeignKey('inOutRecord.come_time'))
    satisfaction = db.Column(db.Numeric(1))
    needCall = db.Column(db.Numeric(1))
    def __init__(self, come_time, satisfaction=None, needCall=None):
        self.come_time = come_time
        self.satisfaction = satisfaction
        self.needCall = needCall
    def __repr__(self):
        return '%s,%s,%s' % (self.come_time, self.satisfaction, self.needCall)

class product (db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True, nullable=False)
    product_name = db.Column(db.String(50))
    recommend_prod_id = db.Column(db.Integer)
    product_pic_url = db.Column(db.String(255))
    product_url = db.Column(db.String(255))
    price = db.Column(db.Integer)
    def __init__(self, product_name, recommend_prod_id, product_pic_url, product_url, price):
        self.product_name = product_name
        self.recommend_prod_id = recommend_prod_id
        self.product_pic_url = product_pic_url
        self.product_url = product_url
        self.price = price
    def __repr__(self):
        return '%s,%s,%s,%s,%s' % (self.product_name, self.recommend_prod_id, self.product_pic_url, self.product_url, self.price)

class orderList (db.Model):
    __tablename__ = 'orderList'
    purchase_no = db.Column(db.Integer, primary_key=True, nullable=False)
    come_time = db.Column(db.DateTime, db.ForeignKey('inOutRecord.come_time'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer)
    def __init__(self, come_time, product_id, quantity):
        self.come_time = come_time
        self.product_id = product_id
        self.quantity = quantity
    def __repr__(self):
        return '%s,%s,%s' % (self.come_time, self.product_id, self.quantity)

# APP ###########################################
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

@handler.add(FollowEvent)
def handle_follow_event(event):
    try:
        # 會員綁定賴帳戶檢查
        user_id = event.source.user_id
        judge_id = customer.query.filter(customer.line == user_id)
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
    if re.match('(09\d{8})', event.message.text):
        user_id = event.source.user_id
        sign_data = event.message.text
        connection = customer.query.filter(customer.phone == sign_data)
        if connection.one_or_none() != None:
            customer.query.filter(customer.phone == sign_data).update({'line': user_id})
            db.session.commit()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Connect Successfully."))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Not Found, Please Try Again."))
    else:
        pass

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
    # surveyTemplate function
    elif event.postback.data.find('[surveyTemplate]') == 0:
        satisfaction = re.match('\[surveyTemplate\](\d),(\d\d\d\d-\d\d-\d\d\s\d\d:\d\d:\d\d)', event.postback.data).group(1)
        come_time = re.match('\[surveyTemplate\](\d),(\d\d\d\d-\d\d-\d\d\s\d\d:\d\d:\d\d)', event.postback.data).group(2)
        survey.query.filter(survey.come_time == come_time).update({'satisfaction': satisfaction})
        db.session.commit()
        if int(satisfaction) < 3:
            needCall_templateMessage = TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text='很抱歉造成您不好的購物體驗，請問需要客服人員的協助嗎???',
                    actions=[
                        PostbackAction(
                            label='是',
                            text='是',
                            data=f'[needCall]1,{come_time}'
                        ),
                        PostbackAction(
                            label='不用了',
                            text='不用了',
                            data=f'[needCall]0,{come_time}'
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, needCall_templateMessage)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="It's our pleasure."))
    elif event.postback.data.find('[needCall]') == 0:
        needCall = re.match('\[needCall\](\d),(\d\d\d\d-\d\d-\d\d\s\d\d:\d\d:\d\d)', event.postback.data).group(1)
        come_time = re.match('\[needCall\](\d),(\d\d\d\d-\d\d-\d\d\s\d\d:\d\d:\d\d)', event.postback.data).group(2)
        survey.query.filter(survey.come_time == come_time).update({'needCall': needCall})
        db.session.commit()
        if int(needCall) == 1:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請稍待，我們將通知客服人員盡快與您聯繫"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="好的，如果有任何意見，歡迎寫信到customer_service@eatice.com.tw"))

UNRECOMMENDED_STATUS = inOutRecord.query.filter(inOutRecord.in_out != 2)
OUT_STATUS = 0
IN_STATUS = 1
RECOMMEND_FINISHED = 2
if UNRECOMMENDED_STATUS.one_or_none():
    come_time = UNRECOMMENDED_STATUS.first().come_time
    phone = inOutRecord.query.filter(inOutRecord.come_time == come_time).one().phone
    status = inOutRecord.query.filter(inOutRecord.come_time == come_time).one().in_out
    line = customer.query.filter(customer.phone == phone).one().line
    # make sure we have buyer's line_id
    if line != None:
        # in situation
        if status == IN_STATUS:
            # push bestSell_templateMessage
            bestSell_sql = '''
                 SELECT product_id, SUM(quantity) as sum
                 FROM orderList
                 WHERE come_time > DATE_SUB(NOW(), INTERVAL 30 DAY)
                 GROUP BY product_id
                 ORDER BY sum DESC LIMIT 5'''
            result = db.engine.execute(text(bestSell_sql))
            columns = []  # for CarouselTemplate
            for i in result:
                product_id = i['product_id']
                uri = product.query.filter(product.product_id == product_id).one().product_url
                thumbnail_image_url = product.query.filter(
                    product.product_id == product_id).one().product_pic_url
                text = product.query.filter(product.product_id == product_id).one().product_name
                carouselColumn = CarouselColumn(
                    thumbnail_image_url=thumbnail_image_url,
                    text=text,
                    actions=[
                        URIAction(
                            label='More Information',
                            uri=uri
                        )
                    ]
                )
                columns.append(carouselColumn)
            bestSell_templateMessage = TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(columns=columns)
            )
            line_bot_api.push_message(line, TextSendMessage(text="Welcome! Please refer are our best-selling items below!"))
            line_bot_api.push_message(line, bestSell_templateMessage)
            inOutRecord.query.filter(inOutRecord.come_time == come_time).update({"in_out": RECOMMEND_FINISHED})
            db.session.commit()
        # out situation
        elif status == OUT_STATUS:


            # push receipt and recommend_templateMessage
            body_contents = [] # for receipt
            footer_contents = [] # for receipt
            columns = []  # for CarouselTemplate
            order = orderList.query.filter(orderList.come_time == come_time).group_by(orderList.product_id).limit(10).all()
            for i in order:
                recommend_prod_id = product.query.filter(product.product_id == i.product_id).one().recommend_prod_id
                uri = product.query.filter(product.product_id == recommend_prod_id).one().product_url
                thumbnail_image_url = product.query.filter(product.product_id == recommend_prod_id).one().product_pic_url
                text = product.query.filter(product.product_id == recommend_prod_id).one().product_name
                carouselColumn = CarouselColumn(
                    thumbnail_image_url=thumbnail_image_url,
                    text=text,
                    actions=[
                        URIAction(
                            label='More Information',
                            uri=uri
                        )
                    ]
                )
                columns.append(carouselColumn)
            recommend_templateMessage = TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(columns=columns)
            )
            line_bot_api.push_message(line,TextSendMessage(text="Hey, you may be interesting in these."))
            line_bot_api.push_message(line, recommend_templateMessage)

            # create surveyTemplate data
            addSurvey = survey(come_time)
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
                            data=f'[surveyTemplate]4,{come_time}'
                        ),
                        PostbackAction(
                            label='滿意',
                            text='滿意',
                            data=f'[surveyTemplate]3,{come_time}'
                        ),
                        PostbackAction(
                            label='不滿意',
                            text='不滿意',
                            data=f'[surveyTemplate]2,{come_time}'
                        ),
                        PostbackAction(
                            label='非常不滿意',
                            text='非常不滿意',
                            data=f'[surveyTemplate]1,{come_time}'
                        )
                    ]
                )
            )
            line_bot_api.push_message(line, survey_templateMessage)
            # update status
            inOutRecord.query.filter(inOutRecord.come_time == come_time).update({"in_out": RECOMMEND_FINISHED})
            db.session.commit()