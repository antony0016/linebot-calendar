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


def list_todo(event):
    # session = create_session()
    events = Event.all_event(event.source.user_id)
    events_id = []
    for e in events:
        events_id.append(e.id)
    event_settings = EventSetting.all_event_setting()
    my_es = []
    for es in event_settings:
        if es.event_id in events_id:
            my_es.append(es)
    return TextSendMessage(text="目前有{}項行事曆".format(str(len(my_es))))


def db_test(event):
    session = create_session()
    users = session.query(User).all()
    return TextSendMessage(text="目前用戶有{}個用戶".format(str(len(users))))
