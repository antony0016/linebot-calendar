import json
from datetime import datetime

from flask import request, jsonify, views

from model.db import create_session
from model.todo import Event, EventSetting, EventMember
from public.instance import line_bot_api, flask_instance


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
    event_id = request.args.get('event_id')
    group_id = request.args.get('group_id')
    events = get_event(line_id, event_id, group_id)
    count = 0
    for event in events:
        count += 1 if event.get('status') else 0
    res = jsonify(data=events, remaining=count, status=200, error_msg='')
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
    if event_id is None:
        return jsonify(data={}, status=400, error_msg='event_id is None')
    status = request.args.get('status', 'false', str).lower() == 'true'
    print(status)
    return change_event_status(line_id, event_id, status).to_json()


def change_event_status(line_id, event_id, status):
    response = MyResponse()
    if event_id is None:
        response.error_msg = 'event_id is None'
        response.status = 400
        return response
    session = create_session()
    event = Event.get_event(session, event_id)
    if event is None:
        response.error_msg = 'event not found'
        response.status = 404
        return response
    event.status = status
    session.commit()
    session.close()
    return response


def get_event(line_id, event_id=None, group_id=None):
    session = create_session()
    events = []
    temp_events = Event.all_event(session, line_id)
    for event in temp_events:
        if event_id is not None and int(event_id) != event.id:
            continue
        if group_id is not None and group_id != event.setting.group_id:
            continue
        events.append(event.to_dict())
    session.close()
    return events


def new_event(line_id, data=None):
    session = create_session()
    response = MyResponse()
    if line_id is None or 'type_id' not in data:
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
        for member in data['members']:
            if member['line_id'] not in [m.user.line_id for m in now_members]:
                EventMember.create_or_get(session, event_id, member['line_id'])
        for member in now_members:
            if member.user.line_id not in [m['line_id'] for m in data['members']]:
                EventMember.delete_member_by_event_id_and_line_id(session, event_id, member.user.line_id)
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
