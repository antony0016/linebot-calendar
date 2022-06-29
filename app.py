# Python official imports
import os

# Open source lib imports
from flask import Flask, request, abort
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

# Custom library
# Import models
from model.db import create_db
from model.user import User
from model.todo import Event, EventType, EventMember, EventSetting

# Line bot reply instance
from public.instance import line_bot_api, handler, logger_setting

# event handler
from service.handler import (
    text_message_handler,
    postback_message_handler,
    followed_event_handler,
)

# flask instance
app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

logger_setting(app)


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
    reply = text_message_handler(event)
    line_bot_api.reply_message(event.reply_token, reply)


# postback message handler
@handler.add(PostbackEvent)
def handle_postback_message(event):
    reply = postback_message_handler(event)
    line_bot_api.reply_message(event.reply_token, reply)


# follow event handler
@handler.add(FollowEvent)
def friend_added(event):
    reply = followed_event_handler(event)
    line_bot_api.reply_message(event.reply_token, reply)


if __name__ == "__main__":
    create_db()
    EventType.create_default_event_types()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
