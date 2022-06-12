# models
from model.db import create_session
from model.user import User

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
    new_event = PostbackRequest(model='event', method='create')
    return TemplateSendMessage(
        alt_text='建立行事曆!',
        template=ButtonsTemplate(
            title="要建立哪種行事曆？",
            text="請選擇行事曆類型",
            actions=[
                PostbackTemplateAction(
                    label="代辦事項",
                    data=new_event.dumps(data={'type': 'todo'})
                ),
                PostbackTemplateAction(
                    label="行程",
                    data=new_event.dumps(data={'type': 'event'})
                ),
                PostbackTemplateAction(
                    label="提醒",
                    data=new_event.dumps(data={'type': 'reminder'})
                ),
            ]
        )
    )
    pass


def db_test(event):
    session = create_session()
    users = session.query(User).all()
    return TextSendMessage(text="目前用戶有{}個用戶".format(str(len(users))))
