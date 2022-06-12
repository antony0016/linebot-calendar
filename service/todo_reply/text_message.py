from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from model.db import create_session
from model.user import User

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
    session = create_session()

    return TemplateSendMessage(
        alt_text='建立行事曆!',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="要建立哪種行事曆？",
            text="請選擇行事曆類型",
            actions=[
                PostbackTemplateAction(
                    label="Todo",
                    data="$todo"
                ),
                PostbackTemplateAction(
                    label="行程",
                    data="$event"
                ),
                PostbackTemplateAction(
                    label="提醒",
                    data="$remi"
                ),
            ]
        )
    )
    pass


def db_test(event):
    session = create_session()
    users = session.query(User).all()
    return TextSendMessage(text="目前用戶有{}個用戶".format(str(len(users))))
