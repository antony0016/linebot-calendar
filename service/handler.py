import json

# response define
from public.response import PostbackRequest

# reply processor mapper
from service.sample_reply.triggers import sample_replies
from service.todo_reply.triggers import todo_text_replies, todo_postback_replies

# models
from model.db import create_session
from model.user import User

from linebot.models import (
    # event
    MessageEvent,
    PostbackEvent,
    FollowEvent,

    # message
    TextMessage,
    TextSendMessage,
    ImagemapSendMessage,
    TemplateSendMessage,

    # template
    ButtonsTemplate,
    ConfirmTemplate,
    PostbackTemplateAction,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    CarouselTemplate,
    CarouselColumn,

    # action
    URIImagemapAction,
    DatetimePickerTemplateAction,
    MessageTemplateAction,
    URITemplateAction,
    URIAction,

    # others
    ImagemapArea,
    BaseSize,
)


def text_message_handler(event):
    message = event.message.text
    replies = sample_replies + todo_text_replies
    for reply in replies:
        if reply['trigger'] in message:
            return reply['reply'](event)
    return TextMessage(text="這個訊息我沒辦法回覆ψ(._. )>")


def postback_message_handler(event):
    data = PostbackRequest(raw_data=event.postback.data)
    replies = todo_postback_replies
    for model in replies:
        methods = replies[model]
        if data.model == model and data.method in methods.keys():
            return methods[data.method](event)
    return TextMessage(text="命令出錯了(っ °Д °;)っ")


def followed_event_handler(event):
    line_id = event.source.user_id
    user = User.create_or_get(line_id)
    if user.id is None:
        return TextMessage(text='設定帳號失敗，請嘗試重新加入本帳號!')
    return TextMessage(text='您的line id為{}，歡迎使用本服務'.format(user.line_id))
