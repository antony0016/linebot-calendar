# models
import datetime

from model.db import create_session
from model.user import User
from model.todo import EventType, Event, EventSetting, ShareCode, ShareRecord

# request
from model.response import PostbackRequest
from public.response import default_messages, get_event_settings_response

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
    columns = default_messages['add_event_columns']['group']
    if event.source.type != 'group':
        columns += default_messages['add_event_columns']['single']
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
    is_group: bool = event.source.type == 'group'
    group_id: str = event.source.group_id if is_group else None
    # $title$description$time
    args = message.split('$')
    args.pop(0)
    session = create_session()
    event_type = EventType.get_type_by_name(session, args[0])
    if event_type is None or len(args) < 4:
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
                PostbackTemplateAction(
                    label='是',
                    data=new_data.dumps(data={
                        'type_id': event_type.id,
                        'line_id': line_id,
                        'title': args[1],
                        'description': args[2],
                        'time': args[3],
                        'is_group': is_group,
                        'group_id': group_id,
                    })
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
        return TemplateSendMessage(
            alt_text=event_setting.title,
            template=event_setting.to_line_template()
        )


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


def list_all_todo(event):
    # get events and event settings
    session = create_session()
    line_id = event.source.user_id
    is_group = event.source.type == 'group'
    event_settings = EventSetting.all_event_setting(
        session, line_id, is_group=is_group)
    columns = get_event_settings_response(event_settings, is_group=is_group)
    session.close()
    if len(columns) > 0:
        return TemplateSendMessage(
            alt_text='行事曆列表',
            template=CarouselTemplate(
                columns=columns
            )
        )
    return create_menu(event)


def share_event_list(event):
    # get events and event settings
    session = create_session()
    line_id = event.source.user_id
    is_group = event.source.type == 'group'
    if is_group:
        return TextSendMessage(text='群組無法分享行事曆')
    events = Event.all_event(session, line_id)
    # share all event for other user
    columns = [
        CarouselColumn(
            title='分享全部',
            text='分享全部',
            actions=[
                PostbackTemplateAction(
                    label='分享',
                    data=PostbackRequest(model='share_code', method='create').dumps(data={
                        'event_id': -1,
                    })
                )
            ]
        )
    ]
    for the_event in events:
        columns.append(
            the_event.setting.to_line_template(custom_actions=[
                PostbackTemplateAction(
                    label='分享',
                    data=PostbackRequest(model='share_code', method='create').dumps(data={
                        'event_id': the_event.id,
                    })
                )
            ], convert_action=True, is_column=True)
        )
    session.close()
    if len(columns) > 0:
        return TemplateSendMessage(
            alt_text='行事曆列表',
            template=CarouselTemplate(
                columns=columns
            )
        )
    return create_menu(event)


def show_code_events(event):
    code = event.message.text.replace('@code=', '')
    session = create_session()
    share_code = ShareCode.get_share_code(session, code)
    if share_code is None:
        return TextSendMessage(text='分享碼不存在')
    columns = []
    for the_event in share_code.events:
        columns.append(
            the_event.setting.to_line_template(custom_actions=[
                MessageTemplateAction(
                    label='來源',
                    text='分享人：{}\n分享碼：{}'.format(share_code.share_user.name, share_code.code)
                )
            ], convert_action=True, is_column=True)
        )
    return TemplateSendMessage(
        alt_text='行事曆列表',
        template=CarouselTemplate(
            columns=columns
        )
    )


def db_test(event):
    print(event)
    session = create_session()
    users = session.query(User).all()
    return TextSendMessage(text="目前用戶有{}個用戶".format(str(len(users))))
