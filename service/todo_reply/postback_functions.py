# models
from datetime import datetime, timedelta

from service.todo_reply.text_functions import create_menu
from public.instance import line_bot_api
from model.db import create_session
# linebot imports
from linebot.models import (
    # message
    TextSendMessage,
    TemplateSendMessage,

    # template
    ButtonsTemplate,
    # action
    PostbackTemplateAction,
    DatetimePickerTemplateAction,
    CarouselTemplate,
    CarouselColumn,
    MessageTemplateAction,
    QuickReply,
    QuickReplyButton,
)

from model.todo import Event, EventSetting, EventType, EventMember, ShareCode
# postback request
from model.response import PostbackRequest
from public.response import get_event_details, get_quick_reply


def confirm_todo_content(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    is_group = data.get('group_id', None) is not None
    group_id = data.get('group_id', None)
    session = create_session()
    # create event and event setting at the same time
    event = Event.create_event(
        session, data['type_id'], data['line_id'],
        is_group=is_group, group_id=group_id
    )
    if event.id is None:
        return TextSendMessage(text='建立失敗，請重新嘗試建立行事曆')
    start_time = None
    if data['time'].replace(' ', '') != '':  # if time is not empty
        start_time = datetime.fromisoformat(data['time']) - timedelta(hours=8)
    # update event setting to right content
    EventSetting.update_event_setting(
        session, event.id, title=data['title'],
        description=data['description'],
        start_time=start_time
    )
    event_id = event.id
    type_name = EventType.get_type_by_id(session, data['type_id']).name
    session.close()
    # make quick reply options
    quick_replies = get_quick_reply(event_id)
    return TextSendMessage(text=f'{type_name}: {data["title"]} 建立成功!', quick_reply=QuickReply(
        items=quick_replies,
    ))


def create_event_by_type(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    event = Event.create_event(session, data['type_id'], data['line_id'],
                               is_group=data['is_group'], group_id=data['group_id'])
    if event.id is None:
        return TextSendMessage(text='建立行事曆失敗，請重新嘗試建立')
    event_type = EventType.get_type_by_id(session, data['type_id'])
    new_data = PostbackRequest(model='event', method='update')
    delete_data = PostbackRequest(model='event', method='delete')
    session.close()
    return TemplateSendMessage(
        alt_text=event_type.name + '選項',
        template=ButtonsTemplate(
            title=event_type.name + '選項',
            text='設定' + event_type.name + '選項',
            actions=[
                PostbackTemplateAction(
                    label="細節設定",
                    data=new_data.dumps(data={'event_id': event.id}),
                ),
                PostbackTemplateAction(
                    label="刪除",
                    data=delete_data.dumps(data={"event_id": event.id}),
                ),
            ]
        )
    )


def list_todo_by_type_id(event):
    line_id = event.source.user_id
    is_group = event.source.type == 'group'
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    event_settings = EventSetting.all_event_setting(
        session, line_id, data['type_id'], is_group=is_group
    )
    columns = get_event_details(event_settings, is_group=is_group)

    if len(columns) == 0:
        return create_menu(event)
    return TemplateSendMessage(
        alt_text='查詢',
        template=CarouselTemplate(
            columns=columns,
        )
    )


def simple_reply(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    return TextSendMessage(text=data['text'])


def event_setting_detail(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    the_event = Event.get_event(session, data['event_id'])
    if the_event is None:
        session.close()
        return TextSendMessage(text='找不到對應行事曆，請重新查詢')
    event_setting = the_event.setting
    new_data = PostbackRequest(model='event_setting', method='update')
    reply_data = PostbackRequest(model='reply', method='create')
    session.close()
    event_description = event_setting.description
    event_date = '未設定'
    event_time = '未設定'
    # show event date and time
    if event_setting.start_time is not None:
        event_date = event_setting.start_time.isoformat().split('T')[0]
        event_time = event_setting.start_time.isoformat().split('T')[1]
    columns = [
        CarouselColumn(
            title=event_setting.title + ' 標題',
            text=event_setting.title,
            actions=[
                PostbackTemplateAction(
                    label='重新設定標題',
                    text='*請直接複製機器人的指令，並加上標題文字',
                    data=reply_data.dumps(data={'text': '{}@event.title='.format(the_event.id)}),
                )
            ]
        ),
        CarouselColumn(
            title=event_setting.title + ' 備註',
            text=event_description + ' ',
            actions=[
                PostbackTemplateAction(
                    label='重新設定備註',
                    text='*請直接複製機器人的指令，並加上備註文字',
                    data=reply_data.dumps(data={'text': '{}@event.description='.format(the_event.id)}),
                )
            ]
        ),
        CarouselColumn(
            title=event_setting.title + ' 提醒時間',
            text=event_date + ' ' + event_time,
            actions=[
                DatetimePickerTemplateAction(
                    label='重新設定提醒時間',
                    data=new_data.dumps(data={"event_id": the_event.id, "column": "start_time"}),
                    mode='datetime',
                )
            ]
        ),
    ]
    return TemplateSendMessage(
        alt_text='細節設定',
        template=CarouselTemplate(
            columns=columns,
        )
    )


def delete_event(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    is_delete = Event.delete_event(session, data['event_id'])
    session.close()
    quick_replies = get_quick_reply()
    if not is_delete:
        return TextSendMessage(text='刪除失敗', quick_reply=QuickReply(items=quick_replies))
    return TextSendMessage(text='刪除成功', quick_reply=QuickReply(items=quick_replies))


def update_event_by_event_id(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    event_id, column = data['event_id'], data['column']
    event_setting = None
    reply = TextSendMessage(text='更新成功')
    # if part == 'title':
    #     event_setting = EventSetting.update_event_setting(event_id, title='test')
    # if part == 'description':
    #     event_setting = EventSetting.update_event_setting(event_id, description='test')
    if column == 'start_time':
        raw_start_time = event.postback.params['datetime'] + ':00'
        start_time = datetime.fromisoformat(raw_start_time)
        event_setting = EventSetting.update_event_setting(session, event_id, start_time=start_time)
    if event_setting is None:
        reply = TextSendMessage(text='更新失敗')
    session.close()
    return reply


def list_event_members(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    the_event = Event.get_event(session, data['event_id'])
    if the_event is None:
        return TextSendMessage(text='找不到此活動/代辦事項/提醒')
    event_members, event_setting = the_event.members, the_event.setting
    request = PostbackRequest(model='event_member')
    # join in event option
    columns = [
        CarouselColumn(
            title=event_setting.title,
            text='加入此活動',
            actions=[
                PostbackTemplateAction(
                    label='加入',
                    data=request.dumps(
                        method='create',
                        data={'event_id': the_event.id}
                    ),
                )
            ],
        )
    ]
    # leave event option
    for member in event_members:
        columns.append(CarouselColumn(
            title=event_setting.title,
            text=member.user.name,
            actions=[
                PostbackTemplateAction(
                    label='刪除',
                    data=request.dumps(
                        method='delete',
                        data={'member_id': member.id}
                    ),
                )
            ],
        ))
    session.close()
    return TemplateSendMessage(
        template=CarouselTemplate(columns=columns),
        alt_text='參與成員'
    )


def new_share_code(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    line_id = event.source.user_id
    session = create_session()
    the_event = Event.get_event(session, data['event_id'])
    events = []
    if the_event is None and data['event_id'] != -1:
        return TextSendMessage(text='找不到此活動/代辦事項/提醒')
    if data['event_id'] == -1:
        events = [share_event.id for share_event in Event.all_event(session, line_id)]
    else:
        events = [the_event.id]
    share_code = ShareCode.create_share_code(session, events, line_id)
    response = TextSendMessage(text='@code={}'.format(share_code.code))
    session.close()
    return response


def member_join(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    line_id = event.source.user_id
    the_event = Event.get_event(session, data['event_id'])
    if the_event is None:
        return TextSendMessage(text='找不到此活動/代辦事項/提醒')
    member = EventMember.create_or_get(session, the_event.id, line_id)
    message = '加入成功'
    if member is None:
        message = '加入失敗'
    session.close()
    return TextSendMessage(text=message)


def member_leave(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    de_count = EventMember.delete_member(session, data['member_id'])
    session.close()
    if de_count > 0:
        return TextSendMessage(text='刪除成功')
    return TextSendMessage(text='刪除失敗')


def push_to_group(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    the_event = Event.get_event(session, data['event_id'])
    if the_event is None:
        session.close()
        return TextSendMessage(text='找不到此活動/代辦事項/提醒')
    event_members = the_event.members
    if len(event_members) == 0:
        session.close()
        return TextSendMessage(text='此活動/代辦事項/提醒尚無人參加')
    # line_ids = [member.user.line_id for member in event_members]
    line_bot_api.push_message(the_event.setting.group_id, TemplateSendMessage(
        alt_text=the_event.setting.title + '提醒！',
        template=CarouselTemplate(columns=[
            the_event.setting.to_line_template(True, for_notify=True),
        ])
    ))
    session.close()
    return TextSendMessage(text='已推播至群組', quick_reply=QuickReply(items=get_quick_reply()))
