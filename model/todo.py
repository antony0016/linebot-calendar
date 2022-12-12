from linebot.models import (
    TemplateSendMessage, ButtonsTemplate, CarouselColumn, CarouselTemplate,
    PostbackTemplateAction, URITemplateAction
)

from model.db import create_session
from model.user import User

from datetime import datetime, timedelta

from public.instance import Base, flask_instance

from sqlalchemy import Column, func
from sqlalchemy import Integer, DateTime, String, ForeignKey, Boolean
# from model.db import MyBase
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session

from model.response import PostbackRequest
import secrets


class EventType(Base):
    __tablename__ = 'event_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    name = Column(String, nullable=False)

    events = relationship('Event', back_populates='event_type')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
        }

    @staticmethod
    def create_default_event_types():
        session = create_session()
        event_type_name_list = ['活動', '提醒', '待辦事項']
        for type_name in event_type_name_list:
            event_type = session.query(EventType).filter(EventType.name == type_name).first()
            if event_type is None:
                event_type = EventType(name=type_name)
                session.add(event_type)
        session.commit()
        session.close()

    @staticmethod
    def get_type_by_id(session: Session, type_id):
        event_type = session.query(EventType).filter(EventType.id == type_id).first()
        return event_type

    @staticmethod
    def get_type_by_name(session: Session, name):
        event_type = session.query(EventType).filter(EventType.name == name).first()
        return event_type

    @staticmethod
    def get_types(session: Session):
        event_types = session.query(EventType).all()
        return event_types


class Event(Base):
    __tablename__ = 'event'
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    create_uid = Column(Integer, ForeignKey('user.id'), nullable=False)
    create_user = relationship('User', back_populates='events')

    members = relationship('EventMember', back_populates='event')
    setting = relationship('EventSetting', back_populates='event', uselist=False)

    type_id = Column(ForeignKey('event_type.id'), nullable=False)
    event_type = relationship('EventType', back_populates='events')

    share_code_id = Column(ForeignKey('share_code.id'), nullable=True)
    share_code = relationship('ShareCode', back_populates='events')

    is_done = Column(Boolean, default=False)

    def to_dict(self):
        session = create_session()
        setting = self.setting.to_dict()
        members = [member.to_dict() for member in EventMember.all_member_by_event(session, self.id)]
        session.close()
        return {
            'id': self.id,
            'type_id': self.type_id,
            'type_name': self.event_type.name,
            'title': setting['title'],
            'description': setting['description'],
            'start_time': setting['start_time'],
            'group_id': setting['group_id'],
            'is_group': setting['is_group'],
            'members': members,
            'spots': setting['spots'],
            'is_done': self.is_done,
        }

    @staticmethod
    def all_event(session: Session, line_id):
        user = User.create_or_get(session, line_id)
        events = session.query(Event).filter(Event.create_uid == user.id).all()
        return events

    @staticmethod
    def api_all_event(session: Session):
        events = session.query(Event).filter().all()
        return events

    @staticmethod
    def create_event(session: Session, type_id, line_id, is_group=False, group_id=None):
        event_type = session.query(EventType).filter(EventType.id == type_id).first()
        user = User.create_or_get(session, line_id)
        new_event = Event(create_uid=user.id, type_id=event_type.id)
        session.add(new_event)
        session.commit()

        # create data relate with event.
        EventSetting.create_event_setting(session, new_event.id,
                                          is_group=is_group, group_id=group_id)
        EventMember.create_or_get(session, new_event.id, line_id)
        session.refresh(new_event)
        return new_event

    @staticmethod
    def get_event(session: Session, event_id, group_id=None):
        event = session.query(Event).filter(Event.id == event_id).first()
        if group_id is not None:
            event = session.query(Event).filter(Event.id == event_id, Event.setting.group_id == group_id).first()
        return event

    @staticmethod
    def update_event_type(session: Session, event_id, type_id):
        event = session.query(Event).filter(Event.id == event_id).first()
        event.type_id = type_id
        session.commit()
        return event

    @staticmethod
    def delete_event(session: Session, event_id):
        session.query(EventSetting).filter(EventSetting.event_id == event_id).delete()
        delete_count = session.query(Event).filter(Event.id == event_id).delete()
        session.commit()
        return delete_count > 0


class EventSetting(Base):
    __tablename__ = 'event_setting'
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    event_id = Column(ForeignKey('event.id'), nullable=False, unique=True)
    event = relationship('Event', back_populates='setting')

    is_group = Column(Boolean, default=False)
    group_id = Column(String, nullable=True)
    title = Column(String, default=' ')
    description = Column(String, default=' ')
    start_time = Column(DateTime)

    spots = relationship('EventSpot', back_populates='setting')

    def to_dict(self):
        session = create_session()
        spots = [spot.to_dict() for spot in EventSpot.all_spot_by_event_setting_id(session, self.id)]
        return {
            'id': self.id,
            'create_time': self.create_time,
            'edit_time': self.edit_time,
            'event_id': self.event_id,
            'is_group': self.is_group,
            'group_id': self.group_id,
            'title': self.title,
            'description': self.description,
            'start_time': self.start_time,
            'spots': spots,
        }

    def to_string(self, with_column=True, with_new_line=True, show_short=False):
        sep = '\n' if with_new_line else ' '
        event_date = ' '
        event_time = ' '
        if self.start_time is not None:
            start_time = self.start_time + timedelta(hours=8)
            event_date = start_time.strftime('%Y-%m-%d')
            event_time = start_time.strftime('%H:%M:%S')
        result = f'{"標題：" if with_column else ""}{self.title}{sep}' \
                 f'{"敘述：" if with_column else ""}{self.description}{sep}' \
                 f'{"日期：" if with_column else ""}{event_date}{sep}' \
                 f'{"時間：" if with_column else ""}{event_time}'[0:57]
        if self.event.type_id == 3:
            result = f'{"標題：" if with_column else ""}{self.title}{sep}'
        return result[0:56] + '...' if show_short and len(result) > 56 else result

    def to_line_template(self, is_column=False, custom_actions=None, is_override=False, for_notify=False):
        request = PostbackRequest(model='event', data={'event_id': self.event_id})
        custom_actions = [] if custom_actions is None else custom_actions
        actions = custom_actions
        if not is_override:
            actions += [
                URITemplateAction(
                    label='顯示細節',
                    uri=f'https://liff.line.me/1657271223-2bLxz75P?eventID={self.event_id}',
                ),
                URITemplateAction(
                    label='網頁操作',
                    uri=f'https://liff.line.me/1657271223-3Gz7xDA1?eventID={self.event_id}',
                ),
                PostbackTemplateAction(
                    label="刪除",
                    data=request.dumps(method='delete'),
                ),
            ]
        content = self.to_string(show_short=True)
        template = ButtonsTemplate(
            title=self.title + (' 時間快到了！' if for_notify else ''),
            text=content,
            actions=actions
        )
        if is_column:
            template = CarouselColumn(
                title=self.title + (' 時間快到了！' if for_notify else ''),
                text=content,
                actions=actions
            )
        return template

    @staticmethod
    def all_event_setting(session: Session, line_id, type_id=-1, is_group=False):
        user = User.create_or_get(session, line_id)
        events = session.query(Event).filter(Event.create_uid == user.id).all()
        if type_id == -1:
            events = session.query(Event).filter(Event.create_uid == user.id).all()
        else:
            events = session.query(Event).filter(
                Event.type_id == type_id, Event.create_uid == user.id
            ).all()
        event_settings = []
        for event in events:
            event_setting = session.query(EventSetting) \
                .filter(EventSetting.event_id == event.id).first()
            if event_setting is None:
                continue
            if is_group and event_setting.is_group is False:
                continue
            event_settings.append(event_setting)
        event_settings.reverse()
        return event_settings

    @staticmethod
    def create_event_setting(session: Session, event_id, is_group=False, group_id=None):
        new_event_setting = EventSetting(event_id=event_id, is_group=is_group, group_id=group_id)
        session.add(new_event_setting)
        session.commit()
        return new_event_setting

    @staticmethod
    def get_event_setting_by_event_id(session: Session, event_id, is_group=False):
        if is_group:
            event_setting = session.query(EventSetting).filter(
                EventSetting.event_id == event_id,
                EventSetting.is_group == is_group
            ).first()
        else:
            event_setting = session.query(EventSetting).filter(
                EventSetting.event_id == event_id,
            ).first()
        return event_setting

    @staticmethod
    def update_event_setting(session: Session, event_id, title=None, description=None, start_time: datetime = None,
                             spots=None):
        event_setting = EventSetting.get_event_setting_by_event_id(session, event_id)
        if event_setting is None:
            EventSetting.create_event_setting(session, event_id)
            event_setting = session.query(EventSetting).filter(EventSetting.event_id == event_id).first()
        if title is not None and title != '':
            event_setting.title = title
        if description is not None and description != '':
            event_setting.description = description
        if start_time is not None and start_time != '':
            event_setting.start_time = start_time
        session.commit()
        session.refresh(event_setting)
        return event_setting


class EventMember(Base):
    __tablename__ = 'event_member'
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    event_id = Column(ForeignKey('event.id'), nullable=False)
    event = relationship('Event', back_populates='members')

    user_id = Column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='member')

    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'line_id': self.user.line_id,
        }

    @staticmethod
    def all_member_by_event(session: Session, event_id):
        event_members = session.query(EventMember) \
            .filter(EventMember.event_id == event_id).all()
        return event_members

    @staticmethod
    def create_or_get(session: Session, event_id, line_id):
        user = User.create_or_get(session, line_id)
        event_member = session.query(EventMember) \
            .filter(EventMember.user_id == user.id,
                    EventMember.event_id == event_id).first()
        if event_member is None:
            event_member = EventMember(user_id=user.id, event_id=event_id)
            session.add(event_member)
            session.commit()
        return event_member

    @staticmethod
    def delete_member(session: Session, member_id) -> bool:
        delete_count = session.query(EventMember).filter(
            EventMember.id == member_id
        ).delete()
        session.commit()
        return delete_count > 0

    @staticmethod
    def delete_member_by_event_id_and_line_id(session: Session, event_id, line_id) -> bool:
        delete_count = session.query(EventMember).filter(
            EventMember.event_id == event_id,
            EventMember.user_id == User.create_or_get(session, line_id).id
        ).delete()
        session.commit()
        return delete_count > 0


class ShareCode(Base):
    __tablename__ = 'share_code'
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    events = relationship('Event', back_populates='share_code')

    user_id = Column(ForeignKey('user.id'), nullable=False)
    share_user = relationship('User', back_populates='shared_codes')

    code = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # share_records = relationship('ShareRecord', back_populates='share_code')

    @staticmethod
    def create_share_code(session: Session, event_ids, line_id):
        user = User.create_or_get(session, line_id)
        new_code = secrets.token_hex(16)
        while ShareCode.get_share_code(session, new_code) is not None:
            new_code = secrets.token_hex(16)
        share_code = ShareCode(user_id=user.id, code=new_code)
        session.add(share_code)
        for event_id in event_ids:
            event = session.query(Event).filter(Event.id == event_id).first()
            event.share_code_id = share_code.id
            share_code.events.append(event)
        session.add(share_code)
        session.commit()
        return share_code

    @staticmethod
    def get_share_code(session: Session, code):
        share_code = session.query(ShareCode).filter(ShareCode.code == code).first()
        return share_code


# class ShareRecord(Base):
#     __tablename__ = 'share_record'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     create_time = Column(DateTime, server_default=func.now())
#     edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
#
#     user_id = Column(ForeignKey('user.id'), nullable=False)
#     user = relationship('User', back_populates='share_records')
#
#     share_code_id = Column(ForeignKey('share_code.id'), nullable=False)
#     share_code = relationship('ShareCode', back_populates='share_records')
#
#     @staticmethod
#     def get_record_by_user_id_and_share_code_id(session: Session, user_id, share_code):
#         code = session.query(ShareCode).filter(ShareCode.code == share_code).first()
#         if code is None:
#             return None
#         return session.query(ShareRecord).filter(
#             ShareRecord.user_id == user_id,
#             ShareRecord.share_code_id == code.id
#         ).first()
#
#     @staticmethod
#     def new_record(session: Session, share_code_id, line_id):
#         user = User.create_or_get(session, line_id)
#         share_record = ShareRecord(user_id=user.id, share_code_id=share_code_id)
#         session.add(share_record)
#         session.commit()
#         return share_record


class EventSpot(Base):
    __tablename__ = 'event_spot'
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    setting = relationship('EventSetting', back_populates='spots')
    event_setting_id = Column(ForeignKey('event_setting.id'), nullable=False)
    name = Column(String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'event_setting_id': self.event_setting_id,
            'name': self.name,
        }

    @staticmethod
    def all_spot_by_event_setting_id(session: Session, event_setting_id):
        return session.query(EventSpot).filter(EventSpot.event_setting_id == event_setting_id).all()

    @staticmethod
    def create_or_get(session: Session, event_setting_id, name):
        event_spot = session.query(EventSpot).filter(
            EventSpot.event_setting_id == event_setting_id,
            EventSpot.name == name
        ).first()
        if event_spot is None:
            event_spot = EventSpot(event_setting_id=event_setting_id, name=name)
            session.add(event_spot)
            session.commit()
        return event_spot

    @staticmethod
    def delete(session: Session, event_spot_id):
        delete_count = session.query(EventSpot).filter(
            EventSpot.id == event_spot_id
        ).delete()
        session.commit()
        return delete_count > 0

    @staticmethod
    def delete_by_name(session: Session, event_setting_id, name):
        delete_count = session.query(EventSpot).filter(
            EventSpot.event_setting_id == event_setting_id,
            EventSpot.name == name
        ).delete()
        session.commit()
        return delete_count > 0
