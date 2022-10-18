# models
import datetime

from service.todo_reply.text_functions import create_menu

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

from model.todo import Event, EventSetting, EventType
# postback request
from public.response import PostbackRequest, get_event_settings_response


def create_todo_by_text(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    is_group = event.source.type == 'group'
    session = create_session()
    event = Event.create_event(session, data['type_id'], data['line_id'], is_group=is_group)
    if event.id is None:
        return TextSendMessage(text='建立失敗，請重新嘗試建立行事曆')
    EventSetting.update_event_setting(session, event.id, title=data['title']
                                      , description=data['note']
                                      , start_time=datetime.datetime.fromisoformat(data['time']))
    event_id = event.id
    session.close()
    get_data = PostbackRequest(model='event', method='read')
    update_data = PostbackRequest(model='event', method='update')
    delete_data = PostbackRequest(model='event', method='delete')
    quick_reply_actions = list()
    quick_reply_actions.append(QuickReplyButton(
        action=PostbackTemplateAction(label='查詢行事曆',
                                      data=get_data.dumps(data={'event_id': event_id}))
    ))
    quick_reply_actions.append(QuickReplyButton(
        action=PostbackTemplateAction(label='細節設定',
                                      data=update_data.dumps(data={'event_id': event_id}))
    ))
    quick_reply_actions.append(QuickReplyButton(
        action=PostbackTemplateAction(label='刪除',
                                      data=delete_data.dumps(data={'event_id': event_id}))
    ))
    return TextSendMessage(text='建立成功', quick_reply=QuickReply(
        items=quick_reply_actions,
    ))


def create_event_by_type(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    event = Event.create_event(session, data['type_id'], data['line_id'])
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
    columns = get_event_settings_response(event_settings)
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
    event = Event.get_event(session, data['event_id'])
    if event is None:
        session.close()
        return TextSendMessage(text='好像沒有這個行事曆喔')
    event_type = EventType.get_type_by_id(session, event.type_id)
    new_data = PostbackRequest(model='event_setting', method='update')
    reply_data = PostbackRequest(model='reply', method='create')
    session.close()
    return TemplateSendMessage(
        alt_text=event_type.name + '細節',
        template=ButtonsTemplate(
            title=event_type.name + '細節',
            text='設定' + event_type.name + '細節',
            actions=[
                PostbackTemplateAction(
                    label="設定標題",
                    text='*請直接複製機器人的指令，並加上標題文字',
                    data=reply_data.dumps(data={'text': '{}@event.title='.format(event.id)}),
                ),
                PostbackTemplateAction(
                    label="設定敘述",
                    text='*請直接複製機器人的指令，並加上敘述文字',
                    data=reply_data.dumps(data={'text': '{}@event.description='.format(event.id)}),
                ),
                DatetimePickerTemplateAction(
                    label="設定提醒",
                    data=new_data.dumps(data={"event_id": event.id, "column": "start_time"}),
                    mode='datetime',
                ),
            ]
        )
    )


def delete_event(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    session = create_session()
    is_delete = Event.delete_event(session, data['event_id'])
    session.close()
    if not is_delete:
        return TextSendMessage(text='刪除失敗')
    return TextSendMessage(text='刪除成功')


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
        start_time = event.postback.params['datetime'] + ':00'
        event_setting = EventSetting.update_event_setting(session, event_id, start_time=start_time)
    if event_setting is None:
        reply = TextSendMessage(text='更新失敗')
    session.close()
    return reply


# todo: member_join
def member_join(event):
    return TextSendMessage(text='')


# todo: member_leave
def member_leave(event):
    return TextSendMessage(text='')
