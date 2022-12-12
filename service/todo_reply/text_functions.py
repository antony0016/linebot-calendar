# models
import datetime

from model.db import create_session
from model.user import User
from model.todo import EventType, Event, EventSetting, ShareCode

# request
from model.response import PostbackRequest
from public.response import get_default_message, get_event_details

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
    group_id = None
    if event.source.type == 'group':
        group_id = event.source.group_id
    columns = get_default_message(group_id)
    return TemplateSendMessage(
        alt_text='感謝把我加進群組！請嘗試新增行事曆',
        template=CarouselTemplate(
            columns=columns,
        )
    )


def bot_action_list(event):
    # request = PostbackRequest(model='menu', method='read')
    group_id = event.source.group_id if event.source.group_id else ''
    parameter = ''
    if group_id != '':
        parameter = f'&group_id={group_id}'
    return TemplateSendMessage(
        alt_text='操作列表',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    title='活動相關操作',
                    text='活動相關操作',
                    actions=[
                        # search event
                        URITemplateAction(
                            label='搜尋活動',
                            uri=f'https://liff.line.me/1657271223-yNdXKG7O?typeID=1{parameter}'
                        ),
                        # new event
                        URITemplateAction(
                            label='新增活動',
                            uri=f'https://liff.line.me/1657271223-veVzj6al?typeID=1{parameter}'
                        ),
                        PostbackTemplateAction(
                            label='用linebot查看活動',
                            data='{"model": "event_setting", "method": "read", "data": {"type_id": 1}}'
                        )
                    ]
                ),
                CarouselColumn(
                    title='待辦事項操作',
                    text='待辦事項操作',
                    actions=[
                        # search to-do
                        URITemplateAction(
                            label='搜尋待辦事項',
                            uri=f'https://liff.line.me/1657271223-yNdXKG7O?typeID=3{parameter}'
                        ),
                        # new to-do
                        URITemplateAction(
                            label='新增待辦事項',
                            uri=f'https://liff.line.me/1657271223-veVzj6al?typeID=3{parameter}'
                        ),
                        PostbackTemplateAction(
                            label='用linebot查看待辦事項',
                            data='{"model": "event_setting", "method": "read", "data": {"type_id": 3}}'
                        )
                    ]
                ),
            ]
        )
    )


def create_todo_by_text(event):
    message: str = event.message.text
    line_id: str = event.source.user_id
    is_group: bool = event.source.type == 'group'
    group_id: str = event.source.group_id if is_group else None
    # $type_name$title$description$time
    args = message.split('$')[1:]
    if args[0] == '待辦事項':
        if len(args) == 2:
            args += [' ', ' ']
        else:
            return TextSendMessage(text='請輸入正確格式！')
    if len(args) != 4:
        return TextSendMessage(text='請輸入正確格式！')
    type_name, title, description, time = args
    session = create_session()
    event_type = EventType.get_type_by_name(session, type_name)
    if event_type is None:
        session.close()
        return TextSendMessage(text='找不到該行事曆類型 請重試')
    request = PostbackRequest(model='event', method='create')
    confirm_text = f'標題：{title}\n備註：{description}\n時間：{time}'
    if args[0] == '待辦事項':
        confirm_text = f'待辦事項：{title}'
    session.close()
    return TemplateSendMessage(
        alt_text='確認細節',
        template=ConfirmTemplate(
            text=confirm_text[:299],
            actions=[
                PostbackTemplateAction(
                    label='是',
                    data=request.dumps(
                        model='event_text',
                        method='create',
                        data={
                            'type_id': event_type.id,
                            'line_id': line_id,
                            'title': title,
                            'description': description,
                            'time': time,
                            'group_id': group_id,
                        }
                    )
                ),
                PostbackTemplateAction(
                    label='否',
                    data=request.dumps(
                        model='menu',
                        method='read',
                        data={}
                    ),
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


def group_event_edit_options(event):
    # line_id = event.source.user_id
    request = PostbackRequest(model='event')
    return TemplateSendMessage(
        alt_text='選擇操作',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    title='查看活動', text='查看活動',
                    actions=[
                        MessageTemplateAction(
                            alt_text='快速查看行事曆',
                            label='快速查看行事曆',
                            text='List'
                        ),
                        URITemplateAction(
                            label='查看行事曆',
                            uri='https://liff.line.me/1657271223-yNdXKG7O'
                        )
                    ]
                ),
                CarouselColumn(
                    title='新建', text='新建行事曆',
                    actions=[
                        PostbackTemplateAction(
                            label='指令建立',
                            data=request.dumps(method='menu', data={})
                        ),
                        URITemplateAction(
                            label='網頁建立',
                            uri='https://liff.line.me/1657271223-veVzj6al?typeID=2'
                        )
                    ]
                ),
            ]
        ))


def reminder_edit_options(event):
    # line_id = event.source.user_id
    group_id = ''
    is_group = event.source.type == 'group'
    group_id = event.source.group_id if is_group else None
    request = PostbackRequest(model='event')
    return TemplateSendMessage(
        alt_text='選擇操作',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    title='查看行事曆', text='查看行事曆',
                    actions=[
                        MessageTemplateAction(
                            alt_text='快速查看行事曆',
                            label='快速查看行事曆',
                            text='List'
                        ),
                        URITemplateAction(
                            label='查看行事曆',
                            uri='https://liff.line.me/1657271223-yNdXKG7O'
                        )
                    ]
                ),
                CarouselColumn(
                    title='新建行事曆', text='新建行事曆',
                    actions=[
                        PostbackTemplateAction(
                            label='指令建立',
                            data=request.dumps(method='menu', data={})
                        ),
                        URITemplateAction(
                            label='網頁建立',
                            uri='https://liff.line.me/1657271223-veVzj6al?typeID=2'
                        )
                    ]
                ),
            ]
        ))


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
    is_group = event.source.type == 'group'
    for event_type in event_types:
        if is_group and event_type.id == 2:
            continue
        elif not is_group and event_type.id == 1:
            continue
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
        session, line_id, is_group=is_group
    )
    columns = get_event_details(event_settings, is_group=is_group)
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
            ], is_override=True, is_column=True)
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
            ], is_override=True, is_column=True)
        )
    return TemplateSendMessage(
        alt_text='行事曆列表',
        template=CarouselTemplate(
            columns=columns
        )
    )


def my_console(event):
    session = create_session()
    events = Event.api_all_event(session)
    events.reverse()
    console_events = []
    data = PostbackRequest(model='notify', method='push')
    for the_event in events:
        if the_event.setting.group_id is None:
            continue
        console_events.append(CarouselColumn(
            title=the_event.setting.title,
            text=the_event.setting.description,
            actions=[
                PostbackTemplateAction(
                    label='推播',
                    data=data.dumps(data={'event_id': the_event.id}),
                )
            ]
        ))
    session.close()
    return TemplateSendMessage(
        alt_text='我的控制台',
        template=CarouselTemplate(
            columns=console_events
        )
    )


def db_test(event):
    print(event)
    session = create_session()
    users = session.query(User).all()
    return TextSendMessage(text="目前用戶有{}個用戶".format(str(len(users))))
