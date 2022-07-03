# models
from model.db import create_session
from model.user import User
from model.todo import EventType, Event, EventSetting

# request
from public.response import PostbackRequest

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

    # others
    ImagemapArea,
    BaseSize,
)


def create_todo(event):
    line_id = event.source.user_id
    new_event = PostbackRequest(model='event', method='create')
    event_types = EventType.get_types()
    actions = []
    for event_type in event_types:
        actions.append(
            PostbackTemplateAction(
                label=event_type.name,
                data=new_event.dumps(data={'type_id': event_type.id, 'line_id': line_id})
            )
        )
    return TemplateSendMessage(
        alt_text='建立行事曆!',
        template=ButtonsTemplate(
            title="要建立哪種行事曆？",
            text="請選擇行事曆類型",
            actions=actions,
        )
    )


def update_todo(event):
    line_id = event.source.user_id
    commands = event.message.text.split('@event.')
    if len(commands) <= 1:
        return TextSendMessage(text='指令有誤 請重試')
    event_id = commands[0]
    event_dict = commands[1].split('=')
    if len(event_dict) <= 1:
        return TextSendMessage(text='指令有誤 請重試')
    column, data = event_dict[0], event_dict[1]
    event_setting = None
    if column == 'title':
        event_setting = EventSetting.update_event_setting(event_id, title=data)
    elif column == 'description':
        event_setting = EventSetting.update_event_setting(event_id, description=data)

    if event_setting is None:
        return TextSendMessage(text='更新失敗 請重試')
    else:
        return TextSendMessage(text='更新成功')


def list_todo(event):
    # session = create_session()
    events = Event.all_event(event.source.user_id)
    events_id = []
    for e in events:
        events_id.append(e.id)
    event_settings = EventSetting.all_event_setting()
    my_event_settings = []
    for event_setting in event_settings:
        if event_setting.event_id in events_id:
            my_event_settings.append(event_setting)
    columns = []
    for event_setting in my_event_settings[:10]:
        new_data = PostbackRequest(model='event_setting', method='update')
        columns.append(CarouselColumn(
            title=str(event_setting.title) + '.',
            text=str(event_setting.description) + '.',
            actions=[
                MessageTemplateAction(
                    label="設定標題",
                    text='請直接複製下一行，並加上標題文字\n{}@event.title='.format(event_setting.event_id),
                ),
                MessageTemplateAction(
                    label="設定敘述",
                    text='請直接複製下一行，並加上敘述文字\n{}@event.description='.format(event_setting.event_id),
                ),
                DatetimePickerTemplateAction(
                    label="設定提醒",
                    data=new_data.dumps(data={"event_id": event_setting.event_id, "column": "start_time"}),
                    mode='datetime',
                ),
            ]
        ))
    columns.reverse()
    # return TextSendMessage(text="目前有{}項行事曆".format(str(len(my_event_settings))))
    return TemplateSendMessage(
        alt_text='行事曆列表',
        template=CarouselTemplate(
            columns=columns
        )
    )


def db_test(event):
    session = create_session()
    users = session.query(User).all()
    return TextSendMessage(text="目前用戶有{}個用戶".format(str(len(users))))
