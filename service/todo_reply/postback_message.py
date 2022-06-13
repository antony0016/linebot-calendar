# models
import json

from model.db import create_session
from model.user import User
from model.todo import Event, EventType, EventMember, EventSetting

# postback request
from public.response import PostbackRequest

# linebot imports
from linebot.models import (
    # message
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

)


def create_event_by_type(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    params = json.dumps(event.postback.params)
    data.data['params'] = params
    event = Event.create_event(data['type_id'], data['line_id'])
    if event.id is None:
        return TextSendMessage(text='建立行事曆失敗，請重新嘗試建立')

    new_data = PostbackRequest(model='event_setting', method='update')
    return TemplateSendMessage(
        alt_text='建立行事曆成功!',
        template=ButtonsTemplate(
            title="繼續設定行事曆細節吧!",
            text="繼續設定行事曆細節吧!",
            actions=[
                PostbackTemplateAction(
                    label="設定標題",
                    data=event.dumps(data={'event_id': event.id})
                ),
                PostbackTemplateAction(
                    label="設定敘述",
                    data=event.dumps(data={'event_id': event.id})
                ),
                DatetimePickerTemplateAction(
                    label="設定提醒",
                    data=new_data.dumps({'event_id': event.id}),
                    mode='datetime',
                    initial='1990-01-01',
                    max='2019-03-10',
                    min='1930-01-01'
                ),
            ]
        )
    )
