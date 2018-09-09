from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent
)
import json

app = Flask(__name__)

secretFileContentJson=json.load(open("./line_secret_key", 'r'))
CHANNEL_ACCESS_TOKEN = secretFileContentJson.get("Channel_access_token")
CHANNEL_SECRET = secretFileContentJson.get("Channel_secret")

# yet to be used
''' 
MY_USER_ID = secretFileContentJson.get("My_user_ID")
CHANNEL_ID = secretFileContentJson.get("Channel_ID")
RICH_MENU_ID = secretFileContentJson.get("Rich_menu_ID")
SERVER_URL = secretFileContentJson.get("Server_URL")
'''

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

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
    except LineBotApiError as e:
        app.logger.exception(e)
    if user_id : # 如果對的到user_id的資訊，就代表是被unfollow又再回來
        line_bot_api.reply_message(event.reply_token,
        TextSendMessage(text="T^T...親，你終於回來了！我想您想的好苦啊！！！")) # WELCOME BACK！吃冰之家永遠為您敞開！
    else: # 如果對不到user_id的資訊，就代表是新會員（進行資料庫寫入）
        line_bot_api.reply_message(event.reply_token,
        TextSendMessage(text="歡迎加入吃冰大家族！，請輸入註冊電話或者信箱以進行綁定"))
        # 寫入資料庫動作

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
