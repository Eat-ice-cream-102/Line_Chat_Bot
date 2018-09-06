from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import json

app = Flask(__name__)

secretFileContentJson=json.load(open("/home/mollie/PycharmProjects/LineChatBot/line_secret_key", 'r'))
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
