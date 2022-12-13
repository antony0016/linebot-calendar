import json
from datetime import datetime, timedelta

from flask import request, jsonify, views

from model.db import create_session
from model.todo import Event, EventSetting, EventMember, EventSpot
from public.instance import line_bot_api, flask_instance

from linebot.models import (
    TemplateSendMessage,
    CarouselTemplate,
)


# class UserView(views.MethodView):
#
#     def get(self):
#         return jsonify({'hello': 'world'})


# class GroupView(views.MethodView):
#
#     def get(self, line_id, group_id):
#         # member_ids = line_bot_api.get_group_member_ids(group_id)
#         return jsonify('not implement yet')


class MyResponse:
    def __init__(self, data=None, status=200, error_msg=''):
        if data is None:
            data = {}
        self.data = data
        self.status = status
        self.error_msg = error_msg

    def to_json(self):
        return jsonify(self.__dict__)


@flask_instance.route('/event/list/<line_id>', methods=['POST'])
def list_event_view(line_id):
    event_id = request.args.get('event_id', None, int)
    group_id = request.args.get('group_id')
    type_id = request.args.get('type_id', None, int)
    events = get_event(line_id, event_id, group_id, type_id)
    data = []
    count = 0
    for event in events:
        count += 0 if event.get('is_done') else 1
        data.append(event)
    res = jsonify(data=data, remaining=count, status=200, error_msg='')
    return res


@flask_instance.route('/event/create/<line_id>', methods=['POST'])
def create_event_view(line_id):
    return new_event(line_id, request.form.to_dict()).to_json()


@flask_instance.route('/event/update/<line_id>/<event_id>', methods=['POST'])
def update_event_view(line_id, event_id=None):
    return update_event(line_id, event_id, request.form.to_dict()).to_json()


@flask_instance.route('/event/delete/<line_id>/<event_id>', methods=['POST'])
def delete_event_view(line_id, event_id=None):
    return delete_event(line_id, event_id).to_json()


@flask_instance.route('/event/status/<line_id>/<event_id>', methods=['POST'])
def update_event_status_view(line_id, event_id=None):
    is_done = request.args.get('is_done', 'false', str).lower() != 'false'
    print(is_done)
    return change_event_status(line_id, event_id, is_done).to_json()


@flask_instance.route('/event/notify/check', methods=['GET'])
def check_notify():
    check_event_time()
    return jsonify('ok')


def change_event_status(line_id, event_id, is_done: bool):
    response = MyResponse()
    if event_id is None:
        response.error_msg = 'event_id is None'
        response.status = 400
        return response
    session = create_session()
    event = Event.get_event(session, event_id)
    if event is None:
        response.error_msg = 'event not found'
        response.status = 400
        return response
    event.is_done = is_done
    session.add(event)
    session.commit()
    session.close()
    return response


def get_event(line_id, event_id: int = None, group_id: str = None, type_id: int = None):
    session = create_session()
    events = []
    temp_events = Event.api_all_event(session)
    for event in temp_events:
        if event_id is not None and event_id != event.id:
            continue
        if group_id is not None and group_id != event.setting.group_id:
            continue
        if type_id is not None and type_id != event.type_id:
            continue
        events.append(event.to_dict())
    session.close()
    return events


def new_event(line_id, data=None):
    session = create_session()
    response = MyResponse()
    if line_id is None or 'type_id' not in data.keys():
        response.error_msg = 'line_id or type_id is None'
        response.status = 400
        return response
    is_group = 'group_id' in data
    group_id = data['group_id'] if 'group_id' in data else None
    events = [Event.create_event(session, data['type_id'], line_id, is_group, group_id)]
    if 'title' in data:
        EventSetting.update_event_setting(session, events[0].id, title=data['title'])
    if 'description' in data:
        EventSetting.update_event_setting(session, events[0].id, description=data['description'])
    if 'start_time' in data:
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        EventSetting.update_event_setting(session, events[0].id, start_time=start_time)
    if 'spots' in data:
        for spot in json.loads(data['spots']):
            EventSpot.create_or_get(session, events[0].setting.id, spot['name'])
    if 'members' in data:
        print(data['members'])
        for member in json.loads(data['members']):
            if 'line_id' in member:
                EventMember.create_or_get(session, events[0].id, member['line_id'])
    response.data = [event.to_dict() for event in events]
    session.close()
    return response


def update_event(line_id, event_id, data):
    session = create_session()
    response = MyResponse()
    if line_id is None or event_id is None:
        response.error_msg = 'line_id or event_id is None'
        response.status = 400
        return response
    event = Event.get_event(session, event_id)
    if event is None:
        response.error_msg = 'event not found'
        response.status = 400
        return response
    if 'title' in data:
        EventSetting.update_event_setting(session, event_id, title=data['title'])
    if 'description' in data:
        EventSetting.update_event_setting(session, event_id, description=data['description'])
    if 'start_time' in data:
        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        EventSetting.update_event_setting(session, event_id, start_time=start_time)
    if 'type_id' in data:
        Event.update_event(session, event_id, type_id=data['type_id'])
    if 'members' in data:
        now_members = EventMember.all_member_by_event(session, event_id)
        new_members = json.loads(data['members'])
        now_member_line_ids = [member.user.line_id for member in now_members]
        new_member_line_ids = [member['line_id'] for member in new_members]
        for new_member in new_members:
            if new_member['line_id'] not in now_member_line_ids:
                EventMember.create_or_get(session, event_id, new_member['line_id'])
        for now_member in now_members:
            if now_member.user.line_id not in new_member_line_ids:
                EventMember.delete_member_by_event_id_and_line_id(session, event_id, now_member.user.line_id)
    if 'spots' in data:
        now_spots = EventSpot.all_spot_by_event_setting_id(session, event.setting.id)
        new_spots = json.loads(data['spots'])
        for now_spot in now_spots:
            EventSpot.delete_by_name(session, event.setting.id, now_spot.name)
        for spot in new_spots:
            EventSpot.create_or_get(session, event.setting.id, spot['name'])
    event = Event.get_event(session, event_id)
    response.data = [event.to_dict()]
    session.close()
    return response


def delete_event(line_id, event_id=None):
    response = MyResponse()
    if event_id is None:
        response.error_msg = 'event_id is None'
        response.status = 400
        return response
    session = create_session()
    delete_count = Event.delete_event(session, event_id)
    session.commit()
    session.close()
    if delete_count == 0:
        response.error_msg = 'event not found'
    else:
        response.data = {'delete_count': delete_count}
    return response


def check_event_time():
    session = create_session()
    events = Event.api_all_event(session)
    print(events)
    for event in events:
        if event.setting.start_time is not None and event.setting.start_time < datetime.now():
            time_diff = datetime.now() - event.setting.start_time
            if time_diff.seconds <= 60:
                line_bot_api.push_message(event.create_user.line_id, TemplateSendMessage(
                    alt_text=event.setting.title + '提醒！',
                    template=CarouselTemplate(columns=[
                        event.setting.to_line_template(True, for_notify=True),
                    ])
                ))
                if event.setting.group_id is not None:
                    line_bot_api.push_message(event.setting.group_id, TemplateSendMessage(
                        alt_text=event.setting.title + '提醒！',
                        template=CarouselTemplate(columns=[
                            event.setting.to_line_template(True, for_notify=True),
                        ])
                    ))
    session.close()
