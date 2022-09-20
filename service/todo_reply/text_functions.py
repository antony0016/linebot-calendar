# models
import datetime

from model.db import create_session
from model.user import User
from model.todo import EventType, Event, EventSetting

# request
from public.response import PostbackRequest, normal_messages, get_event_settings

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


# use text to crud event

def create_menu(event):
    columns = normal_messages['add_event_columns']['group']
    if event.source.type != 'group':
        columns += normal_messages['add_event_columns']['single']
    reply = TemplateSendMessage(
        alt_text='感謝把我加進群組！',
        template=CarouselTemplate(
            columns=columns,
        )
    )
    return reply


def confirm_todo_by_text(event):
    message: str = event.message.text
    line_id: str = event.source.user_id
    args = message.split('$')
    args.pop(0)
    session = create_session()
    event_type = EventType.get_type_by_name(session, args[0])
    if event_type is None:
        session.close()
        return TextSendMessage(text='指令錯誤, 請重新參考正確指令')
    new_data = PostbackRequest(method='create', model='event_text')
    get_menu = PostbackRequest(method='read', model='menu')
    confirm_text = """名稱：{}
備註：{}
時間：{}""".format(args[1], args[2], args[3])
    session.close()
    return TemplateSendMessage(
        alt_text='確認細節',
        template=ConfirmTemplate(
            text=confirm_text,
            actions=[
                # MessageTemplateAction(
                #     text='a',
                #     label='y',
                # ),
                # MessageTemplateAction(
                #     text='b',
                #     label='n',
                # ),
                PostbackTemplateAction(
                    label='是',
                    data=new_data.dumps(data={
                        'type_id': event_type.id,
                        'line_id': line_id,
                        'title': args[1],
                        'note': args[2],
                        'time': args[3], })
                ),
                PostbackTemplateAction(
                    label='否',
                    data=get_menu.dumps(data={}),
                )
            ]
        )
    )


# use the postback data to crud event

def create_todo(event):
    line_id = event.source.user_id
    new_event = PostbackRequest(model='event', method='create')
    session = create_session()
    event_types = EventType.get_types(session)
    actions = []
    for event_type in event_types:
        actions.append(
            PostbackTemplateAction(
                label=event_type.name,
                data=new_event.dumps(data={'type_id': event_type.id, 'line_id': line_id})
            )
        )
    session.close()
    return TemplateSendMessage(
        alt_text='建立行事曆!',
        template=ButtonsTemplate(
            title="要建立哪種行事曆？",
            text="請選擇行事曆類型",
            actions=actions,
        )
    )


def update_todo(event):
    # split the command
    commands = event.message.text.split('@event.')
    if len(commands) <= 1:
        return TextSendMessage(text='指令有誤 請重試')
    event_id = commands[0]
    event_dict = commands[1].split('=')
    if len(event_dict) <= 1:
        return TextSendMessage(text='指令有誤 請重試')
    column, data = event_dict[0], event_dict[1]
    event_setting = None

    # update event setting
    session = create_session()
    if column == 'title':
        event_setting = EventSetting.update_event_setting(session, event_id, title=data)
    elif column == 'description':
        event_setting = EventSetting.update_event_setting(session, event_id, description=data)
    session.close()
    # make a response
    if event_setting is None:
        return TextSendMessage(text='更新失敗 請重試')
    else:
        return TextSendMessage(text='更新成功')


def list_todo_option(event):
    get_data = PostbackRequest(model='event_setting', method='read')
    columns = [
        CarouselColumn(
            title='查詢全部',
            text='查詢全部',
            actions=[
                PostbackTemplateAction(
                    label='查詢全部',
                    data=get_data.dumps(data={'type_id': -1})
                )
            ]
        )
    ]
    session = create_session()
    event_types = EventType.get_types(session)
    for event_type in event_types:
        columns.append(CarouselColumn(
            title='查詢{}'.format(event_type.name),
            text='查詢{}'.format(event_type.name),
            actions=[
                PostbackTemplateAction(
                    label='查詢{}'.format(event_type.name),
                    data=get_data.dumps(data={'type_id': event_type.id})
                )
            ]
        ))
    session.close()
    return TemplateSendMessage(
        alt_text='查詢',
        template=CarouselTemplate(columns=columns, )
    )


def list_todo(event):
    # get events and event settings
    session = create_session()
    line_id = event.source.user_id
    event_settings = EventSetting.all_event_setting(session, line_id)
    columns = []
    new_data = PostbackRequest(model='event', method='update')
    delete_data = PostbackRequest(model='event', method='delete')
    columns = get_event_settings(event_settings)
    # for event_setting in event_settings[:10]:
    #     event_date = event_setting.start_time.isoformat().split('T')[0]
    #     event_time = event_setting.start_time.isoformat().split('T')[1]
    #     columns.append(CarouselColumn(
    #         title=str(event_setting.title),
    #         text='敘述：{}\n日期：{}\n時間：{}'
    #         .format(str(event_setting.description), event_date, event_time),
    #         actions=[
    #             PostbackTemplateAction(
    #                 label="細節設定",
    #                 data=new_data.dumps(data={'event_id': event_setting.event_id}),
    #             ),
    #             PostbackTemplateAction(
    #                 label="刪除",
    #                 data=delete_data.dumps(data={"event_id": event_setting.event_id}),
    #             ),
    #         ]
    #     ))
    session.close()
    columns.reverse()
    if len(columns) > 0:
        return TemplateSendMessage(
            alt_text='行事曆列表',
            template=CarouselTemplate(
                columns=columns
            )
        )
    return create_menu(event)


def db_test(event):
    session = create_session()
    users = session.query(User).all()
    return TextSendMessage(text="目前用戶有{}個用戶".format(str(len(users))))
