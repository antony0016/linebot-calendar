import json

# response define
from public.response import PostbackRequest, default_messages
from public.instance import line_bot_api

# reply processor mapper
from service.sample_reply.triggers import sample_replies
from service.todo_reply.triggers import todo_text_replies, todo_postback_replies
from service.todo_reply.text_functions import create_menu

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
    if '*' in message:
        TextMessage(text="----------------")
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
    session = create_session()
    User.create_or_get(session, line_id)
    columns = default_messages['add_event_columns']['single'] + default_messages['add_event_columns']['group']
    reply = TemplateSendMessage(
        alt_text='感謝加入本帳號好友！',
        template=CarouselTemplate(
            columns=columns,
        )
    )
    return reply


def joined_event_handler(event):
    if event.source.type == 'group':
        group_id = event.source.group_id
        # push_message = ''
        # user_statistic = ''
        # line_bot_api.push_message(group_id, TextMessage(text=user_statistic))
    return create_menu(event)
