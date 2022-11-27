import json

# response define
from model.response import PostbackRequest
from public.response import get_default_message
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
    return None


def postback_message_handler(event):
    request = PostbackRequest(raw_data=event.postback.data)
    replies = todo_postback_replies
    for model in replies:
        methods = replies[model]
        if request.model == model and request.method in methods.keys():
            return methods[request.method](event)
    return None


def followed_event_handler(event):
    line_id = event.source.user_id
    group_id = None
    if event.source.type == 'group':
        group_id = event.source.group_id
    session = create_session()
    User.create_or_get(session, line_id)
    columns = get_default_message(group_id)
    reply = TemplateSendMessage(
        alt_text='感謝加入本帳號好友！',
        template=CarouselTemplate(
            columns=columns,
        )
    )
    return reply


def joined_event_handler(event):
    return create_menu(event)
