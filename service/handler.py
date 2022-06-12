import json

from public.response import PostbackRequest

# reply processor mapper
from service.sample_reply.reply import sample_replies
from service.todo_reply.reply import todo_replies, function_mapper

# models
from model.db import create_session
from model.user import User

from linebot.models import (
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


# 處理訊息
def text_message_handler(event):
    message = event.message.text
    for reply in sample_replies + todo_replies:
        if reply['message'] in message:
            return reply['reply'](event)
    return TextMessage(text="這個訊息我沒辦法回覆ψ(._. )>")


def postback_message_handler(event):
    raw_data = event.postback.data
    data = PostbackRequest(raw_data=raw_data)

    for model, methods in function_mapper:
        if data.model == model and data.method in methods.keys():
            return methods[data.method](event)
    return TextMessage(text="命令出錯了(っ °Д °;)っ")


def followed_event_handler(event):
    session = create_session()
    user_line_id = event.source.user_id
    users = session.query(User).filter(User.line_id == user_line_id).all()
    # user = session.query(User).filter(User.line_id == 'user_line_id').first()
    # print(users, user)
    if len(users) == 0:
        new_user = User(line_id=user_line_id)
        session.add(new_user)
        session.commit()
        return TextMessage(text='您的line id為{}, 歡迎加入此官方帳號'.format(user_line_id))
    return TextMessage(text='您的line id為{}'.format(users[0].line_id))
