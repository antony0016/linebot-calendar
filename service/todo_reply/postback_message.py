# models
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
    new_event = PostbackRequest(raw_data=event.postback.data)

    return TemplateSendMessage(
        alt_text='建立行事曆!',
        template=ButtonsTemplate(
            title="要建立哪種行事曆？",
            text="請選擇行事曆類型",
            actions=[
                PostbackTemplateAction(
                    label="代辦事項",
                    data=event.dumps(data={'type': 'todo'})
                ),
            ]
        )
    )
    pass
