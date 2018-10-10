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
import json, time, re, requests, os

# APP.INSTANCE
app = Flask(__name__, instance_relative_config=True, static_url_path='/static')
app.config['DEBUG'] = None

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
pymysql.install_as_MySQLdb()
mysql_key = json.load(open("./requirements/mysql_key", 'r'))
HOST = mysql_key.get('Host')
USER = mysql_key.get("User")
PASSWD = mysql_key.get("Passwd")
DB = mysql_key.get("DB")
CHARTSET = "utf8"

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
class member(db.Model):
    __tablename__ = 'member'
    phone_number = db.Column(db.String(10), primary_key=True)
    member_name = db.Column(db.String(20), nullable=False)
    line_account = db.Column(db.String(255), unique=True)
    birthdate = db.Column(db.DateTime)
    e_mail = db.Column(db.String(50), unique=True)
    credit_card = db.Column(db.String(50))
    photo = db.Column(db.String(255))
    member_password = db.Column(db.String(255))
    has_confirmed = db.Column(db.Boolean)
    c_time = db.Column(db.DateTime)
    has_photo = db.Column(db.Boolean)
    gender = db.Column(db.Integer)
    def __init__(self, phone_number, member_name):
        self.phone_number = phone_number
        self.member_name = member_name
    def __repr__(self):
        return '%s,%s' % (self.line_account, self.member_name)

class inorout(db.Model):
    __tablename__ = 'inorout'
    come_time = db.Column(db.DateTime, primary_key=True)
    left_time = db.Column(db.DateTime)
    phone_number = db.Column(db.String(10),db.ForeignKey('member.phone'))
    inorout = db.Column(db.Integer)
    def __init__(self, come_time, phone_number, inorout):
        self.come_time = come_time
        self.phone_number = phone_number
        self.inorout = inorout
    def __repr__(self):
        return '%s,%s' % (self.phone_number, self.inorout)

class product (db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(50))
    price = db.Column(db.Integer)
    category_no = db.Column(db.Integer)
    stock = db.Column(db.Integer)
    product_url = db.Column(db.String(255))
    picture_url = db.Column(db.String(255))
    re_product_id = db.Column(db.Integer)
    def __init__(self, product_name, re_product_id, picture_url, product_url, price):
        self.product_name = product_name
        self.re_product_id = re_product_id
        self.picture_url = picture_url
        self.product_url = product_url
        self.price = price
    def __repr__(self):
        return '%s,%s,%s,%s,%s' % (self.product_name, self.re_product_id, self.picture_url, self.product_url, self.price)

class purchase (db.Model):
    __tablename__ = 'purchase'
    purchase_no = db.Column(db.Integer, primary_key=True, nullable=False)
    come_time = db.Column(db.DateTime, db.ForeignKey('inorout.come_time'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    quantity = db.Column(db.Integer)
    satisfaction = db.Column(db.Integer)
    neededcall = db.Column(db.Integer)
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
        judge_id = member.query.filter(member.line_account == user_id)
        # 如果對不到user_id的資訊，就代表是新會員（進行資料庫寫入）
        if judge_id.one_or_none() is None:
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
        connection = member.query.filter(member.phone_number == sign_data)
        if connection.one_or_none() is not None:
            member.query.filter(member.phone_number == sign_data).update({'line_account': user_id})
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
        if event.postback.data[6:] == 'location':
            line_bot_api.reply_message(event.reply_token, LocationSendMessage(title='吃冰', address='320桃園市中壢區中大路300號', latitude=24.967798, longitude=121.191802))
        elif event.postback.data[6:] == 'web':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='https://192.168.196.59:8888/index/'))
        elif event.postback.data[6:] == 'customerService':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='Any comment is welcome.\nTel: 03-1231231\nE-mail: customerService@eatice.com.tw'))
    # surveyTemplate function
    elif event.postback.data.find('[surveyTemplate]') == 0:
        satisfaction = re.match('\[surveyTemplate\](\d),(\d\d\d\d-\d\d-\d\d\s\d\d:\d\d:\d\d)', event.postback.data).group(1)
        come_time = re.match('\[surveyTemplate\](\d),(\d\d\d\d-\d\d-\d\d\s\d\d:\d\d:\d\d)', event.postback.data).group(2)
        purchase.query.filter(purchase.come_time == come_time).update({'satisfaction': satisfaction})
        db.session.commit()
        if int(satisfaction) < 3:
            neededcall_templateMessage = TemplateSendMessage(
                alt_text='Confirm template',
                template=ConfirmTemplate(
                    text='很抱歉造成您不好的購物體驗，請問需要客服人員的協助嗎???',
                    actions=[
                        PostbackAction(
                            label='是',
                            text='是',
                            data=f'[neededcall]1,{come_time}'
                        ),
                        PostbackAction(
                            label='不用了',
                            text='不用了',
                            data=f'[neededcall]0,{come_time}'
                        ),
                    ]
                )
            )
            line_bot_api.reply_message(event.reply_token, neededcall_templateMessage)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="It's our pleasure."))
    elif event.postback.data.find('[neededcall]') == 0:
        neededcall = re.match('\[neededcall\](\d),(\d\d\d\d-\d\d-\d\d\s\d\d:\d\d:\d\d)', event.postback.data).group(1)
        come_time = re.match('\[neededcall\](\d),(\d\d\d\d-\d\d-\d\d\s\d\d:\d\d:\d\d)', event.postback.data).group(2)
        purchase.query.filter(purchase.come_time == come_time).update({'neededcall': neededcall})
        db.session.commit()
        if int(neededcall) == 1:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請稍待，我們將通知客服人員盡快與您聯繫"))
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="好的，如果有任何意見，歡迎寫信到customer_service@eatice.com.tw"))

'''
# RECOMMEND-SYS SUB-PROGRESSION##################

pid = os.fork()
if pid == 0:

    OUT_STATUS = 0
    IN_STATUS = 1
    RECOMMEND_FINISHED = 2
    while True:
        db.session.commit()
        UNRECOMMENDED_STATUS = inorout.query.filter(inorout.inorout != 2)
        if UNRECOMMENDED_STATUS.first():
            come_time = UNRECOMMENDED_STATUS.first().come_time
            phone_number = inorout.query.filter(inorout.come_time == come_time).one().phone_number
            status = inorout.query.filter(inorout.come_time == come_time).one().inorout
            line_account = member.query.filter(member.phone_number == phone_number).one().line_account
            # make sure we have buyer's line_id
            if line_account is not None:
                # in situation
                if status == IN_STATUS:
                    # push bestSell_templateMessage
                    bestSell_sql = ''''''
                         SELECT product_id, SUM(quantity) as sum
                         FROM purchase
                         WHERE come_time > DATE_SUB(NOW(), INTERVAL 30 DAY)
                         GROUP BY product_id
                         ORDER BY sum DESC LIMIT 5''''''
                    result = db.engine.execute(text(bestSell_sql))
                    columns = []  # for CarouselTemplate
                    for i in result:
                        product_id = i['product_id']
                        uri = product.query.filter(product.product_id == product_id).one().product_url
                        thumbnail_image_url = product.query.filter(
                            product.product_id == product_id).one().picture_url
                        _text = product.query.filter(product.product_id == product_id).one().product_name
                        carouselColumn = CarouselColumn(
                            thumbnail_image_url=thumbnail_image_url,
                            text=_text,
                            actions=[
                                URIAction(
                                    label='More Information',
                                    uri=f'https://www.Amazon.com/{uri}'
                                )
                            ]
                        )
                        columns.append(carouselColumn)
                    bestSell_templateMessage = TemplateSendMessage(
                        alt_text='Carousel template',
                        template=CarouselTemplate(columns=columns)
                    )
                    line_bot_api.push_message(line_account, TextSendMessage(text="Welcome! Please refer are our best-selling items below!"))
                    line_bot_api.push_message(line_account, bestSell_templateMessage)
                    inorout.query.filter(inorout.come_time == come_time).update({"inorout": RECOMMEND_FINISHED})
                    db.session.commit()
                # out situation
                elif status == OUT_STATUS:
                    # push receipt
                    receipt_item = "Item\n"
                    receipt_unit = "Unit\n"
                    receipt_price = "Price\n"
                    receipt_amount = "Amount\n"
                    total_price = 0
                    full_order = purchase.query.filter(purchase.come_time == come_time).all()
                    for i in full_order:
                        product_name = product.query.filter(product.product_id == i.product_id).one().product_name
                        product_price = product.query.filter(product.product_id == i.product_id).one().price
                        product_unit = i.quantity
                        total_price += product_price*product_unit
                        receipt_item += f"{product_name}\n"
                        receipt_unit += f"{product_unit}\n"
                        receipt_price += f"{product_price}\n"
                        receipt_amount += f"{product_unit*product_price}\n"
                    flexSendContents = BubbleContainer(
                        header=BoxComponent(
                            layout="vertical",
                            contents=[
                                TextComponent(
                                    text="Receipt",
                                    weight="bold"
                                ),
                            ]
                        ),
                        body = BoxComponent(
                            layout="horizontal",
                            spacing="lg",
                            contents=[
                                TextComponent(
                                    text=receipt_item,
                                    wrap=True,
                                    align="start",
                                    flex=0,
                                    size="xxs",
                                    maxLines=1
                                ),
                                TextComponent(
                                    text=receipt_unit,
                                    wrap=True,
                                    align="end",
                                    flex=4,
                                    size="xxs"
                                ),
                                TextComponent(
                                    text=receipt_price,
                                    wrap=True,
                                    align="start",
                                    flex=7,
                                    size="xxs"
                                ),
                                TextComponent(
                                    text=receipt_amount,
                                    wrap=True,
                                    align="start",
                                    flex=8,
                                    size="xxs"
                                )

                            ]
                        ),
                        footer=BoxComponent(
                            layout="horizontal",
                            contents=[
                                TextComponent(
                                    text="Total",
                                    wrap=True,
                                    align="start",
                                    weight="bold"
                                ),
                                TextComponent(
                                    text=f"{total_price}",
                                    wrap=True,
                                    align="end",
                                    weight="bold"
                                )
                            ]
                        )
                    )
                    recipteFlexMessage = FlexSendMessage(alt_text="Flex message", contents=flexSendContents)
                    line_bot_api.push_message(line_account, recipteFlexMessage)
                    # push recommend_templateMessage
                    limit_order = purchase.query.filter(purchase.come_time == come_time).limit(10).all()
                    re_columns = []  # for CarouselTemplate
                    for i in limit_order:
                        re_product_id = product.query.filter(product.product_id == i.product_id).one().re_product_id
                        uri = product.query.filter(product.product_id == re_product_id).one().product_url
                        thumbnail_image_url = product.query.filter(product.product_id == re_product_id).one().picture_url
                        _text = product.query.filter(product.product_id == re_product_id).one().product_name
                        carouselColumn = CarouselColumn(
                            thumbnail_image_url=thumbnail_image_url,
                            text=_text,
                            actions=[
                                URIAction(
                                    label='More Information',
                                    uri=f'https://www.Amazon.com/{uri}'
                                )
                            ]
                        )
                        re_columns.append(carouselColumn)
                    recommend_templateMessage = TemplateSendMessage(
                        alt_text='Carousel template',
                        template=CarouselTemplate(columns=re_columns)
                    )
                    line_bot_api.push_message(line_account, TextSendMessage(text="Hey, you may be interesting in these."))
                    line_bot_api.push_message(line_account, recommend_templateMessage)
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
                    line_bot_api.push_message(line_account, survey_templateMessage)
                    # update status
                    inorout.query.filter(inorout.come_time == come_time).update({"inorout": RECOMMEND_FINISHED})
                    db.session.commit()
        else:
            time.sleep(30)
'''
