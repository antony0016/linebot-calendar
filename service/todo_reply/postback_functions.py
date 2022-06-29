# models
import datetime
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
    ImageCarouselTemplate,
    ImageCarouselColumn,
    CarouselTemplate,
    CarouselColumn,

    # action
    URIImagemapAction,
    PostbackTemplateAction,
    DatetimePickerTemplateAction,
    MessageTemplateAction,
    URITemplateAction,
    URIAction,

)


def create_event_by_type(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    # params = json.dumps(event.postback.params)
    # data['params'] = params
    event = Event.create_event(data['type_id'], data['line_id'])
    if event.id is None:
        return TextSendMessage(text='建立行事曆失敗，請重新嘗試建立')

    new_data = PostbackRequest(model='event_setting', method='update')
    return TemplateSendMessage(
        alt_text='行事曆細節',
        template=ButtonsTemplate(
            title="行事曆細節",
            text="繼續設定行事曆細節",
            actions=[
                MessageTemplateAction(
                    label="設定標題",
                    text='請直接複製下一行，並加上標題文字\n{}@event.title='.format(event.id),
                ),
                MessageTemplateAction(
                    label="設定敘述",
                    text='請直接複製下一行，並加上敘述文字\n{}@event.description='.format(event.id),
                ),
                DatetimePickerTemplateAction(
                    label="設定提醒",
                    data=new_data.dumps(data={"event_id": event.id, "column": "start_time"}),
                    mode='datetime',
                ),
            ]
        )
    )


def update_event_by_event_id(event):
    request = PostbackRequest(raw_data=event.postback.data)
    data = request.data
    event_id, column = data['event_id'], data['column']
    event_setting = None
    message = str(event_id)
    # if part == 'title':
    #     event_setting = EventSetting.update_event_setting(event_id, title='test')
    # if part == 'description':
    #     event_setting = EventSetting.update_event_setting(event_id, description='test')
    if column == 'start_time':
        start_time = event.postback.params['datetime'] + ':00'
        message += start_time
        event_setting = EventSetting.update_event_setting(event_id, start_time=start_time)
    if event_setting is not None:
        return TextSendMessage(text='更新成功')
    return TextSendMessage(text='更新失敗')
