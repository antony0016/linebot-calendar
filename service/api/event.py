import json

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


@flask_instance.route('/event/list/<line_id>', methods=['POST'])
def list_event_view(line_id):
    return get_event(line_id)


@flask_instance.route('/event/retrieve/<line_id>/<event_id>', methods=['POST'])
def retrieve_event_view(line_id, event_id):
    return get_event(line_id, event_id)


@flask_instance.route('/event/create/<line_id>', methods=['POST'])
def create_event_view(line_id):
    return new_event(line_id, request.form.to_dict())


@flask_instance.route('/event/update/<line_id>/<event_id>', methods=['POST'])
def update_event_view(line_id, event_id=None):
    return update_event(line_id, event_id, request.form.to_dict())


@flask_instance.route('/event/delete/<line_id>/<event_id>', methods=['POST'])
def delete_event_view(line_id, event_id=None):
    return update_event(line_id, event_id, request.form.to_dict())


def get_event(line_id, event_id=None):
    session = create_session()
    events = Event.all_event(session, line_id)
    if event_id is not None:
        events = []
        event = Event.get_event(session, event_id)
        if event is not None:
            events.append(event)
    response = jsonify([event.to_dict() for event in events])
    session.close()
    return response


def new_event(line_id, data=None):
    session = create_session()
    if line_id is None or 'type_id' not in data:
        response = jsonify({'error': 'line_id or type_id is None'})
        response.status_code = 400
        return response
    is_group = data['is_group'] if 'is_group' in data else False
    group_id = data['group_id'] if is_group in data else None
    events = [Event.create_event(session, data['type_id'], line_id, is_group, group_id)]
    response = jsonify([event.to_dict() for event in events])
    session.close()
    return response


def update_event(line_id, event_id, data):
    session = create_session()
    if line_id is None or event_id is None:
        response = jsonify({'error': 'line_id or event_id is None'})
        response.status_code = 400
        return response
    event = Event.get_event(session, event_id)
    if event is None:
        response = jsonify({'error': 'event not found'})
        response.status_code = 400
        return response
    data = request.get_json()
    if 'title' in data:
        EventSetting.update_event_setting(session, event_id, title=data['title'])
    if 'description' in data:
        EventSetting.update_event_setting(session, event_id, description=data['description'])
    if 'start_time' in data:
        EventSetting.update_event_setting(session, event_id, start_time=data['start_time'])
    if 'members' in data:
        now_members = EventMember.all_member_by_event(session, event_id)
        for member in data['members']:
            if member['line_id'] not in [m.user.line_id for m in now_members]:
                EventMember.create_or_get(session, event_id, member['line_id'])
        for member in now_members:
            if member.user.line_id not in [m['line_id'] for m in data['members']]:
                EventMember.delete_member_by_event_id_and_line_id(session, event_id, member.user.line_id)
    event = Event.get_event(session, event_id)
    response = jsonify(event.to_dict())
    session.close()
    return response


def delete_event(line_id, event_id=None):
    if event_id is None:
        response = jsonify({'error': 'event_id is None'})
        response.status_code = 400
        return response
    session = create_session()
    delete_count = Event.delete_event(session, event_id)
    session.commit()
    session.close()
    return jsonify({'success': delete_count})
