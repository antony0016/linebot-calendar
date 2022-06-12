# python official imports
import os
from dotenv import load_dotenv, dotenv_values

# open source lib imports
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

# model related imports
from model.db import create_db, create_default_data
from model.user import User
from model.todo import Event, EventType, EventMember, EventSetting

# event handler
from service.handler import (
    text_message_handler,
    postback_message_handler,
    followed_event_handler,
)

DEBUG = True
load_dotenv(dotenv_path='./.env.development') if DEBUG else load_dotenv(dotenv_path='.env')

# flask instance
app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))

# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# text message handler
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    for post_char in ['!', '$', '#', '@', '%']:
        if post_char in event.message.text[:1]:
            return
    reply = text_message_handler(event)
    line_bot_api.reply_message(event.reply_token, reply)


# postback message handler
@handler.add(PostbackEvent)
def handle_postback_message(event):
    for post_char in ['!', '$', '#', '@', '%']:
        if post_char not in event.message.text[:1]:
            return
    reply = postback_message_handler(event)
    line_bot_api.reply_message(event.reply_token, reply)


# follow event handler
@handler.add(FollowEvent)
def friend_added(event):
    reply = followed_event_handler(event)
    line_bot_api.reply_message(event.reply_token, reply)


# @handler.add(MemberJoinedEvent)
# def welcome(event):
#     uid = event.joined.members[0].user_id
#     gid = event.source.group_id
#     profile = line_bot_api.get_group_member_profile(gid, uid)
#     name = profile.display_name
#     message = TextSendMessage(text=f'{name}歡迎加入')
#     line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    create_db()
    create_default_data()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
