import json

from flask import request, jsonify, views

from model.db import create_session
from model.todo import Event, EventSetting, EventMember
from public.instance import line_bot_api


# class UserView(views.MethodView):
#
#     def get(self):
#         return jsonify({'hello': 'world'})


class GroupView(views.MethodView):

    def get(self, line_id, group_id):
        # member_ids = line_bot_api.get_group_member_ids(group_id)
        return jsonify('not implement yet')


class EventView(views.MethodView):

    def get(self, line_id, event_id=None):
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

    def put(self, line_id, event_id):
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
        # {
        #  'title': data['title'],
        #  'description': data['description'],
        #  'start_time': data['start_time'],
        #  'members': [{
        #      'line_id': 'U123456789',
        #  }],
        # }
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

    def delete(self, line_id, event_id=None):
        if event_id is None:
            response = jsonify({'error': 'event_id is None'})
            response.status_code = 400
            return response
        session = create_session()
        delete_count = Event.delete_event(session, event_id)
        session.commit()
        session.close()
        return jsonify({'success': delete_count})
