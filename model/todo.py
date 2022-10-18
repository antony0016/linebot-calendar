from model.db import create_session
from model.user import User

from datetime import datetime

from public.instance import Base, flask_instance

from sqlalchemy import Column, func
from sqlalchemy import Integer, DateTime, String, ForeignKey, Boolean
# from model.db import MyBase
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session


class EventType(Base):
    __tablename__ = 'event_type'
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    name = Column(String, nullable=False)

    events = relationship('Event', back_populates='event_type')

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

    @staticmethod
    def all_event(session: Session, line_id):
        user = User.create_or_get(session, line_id)
        events = session.query(Event).filter(Event.create_uid == user.id).all()
        return events

    @staticmethod
    def create_event(session: Session, type_id, line_id, is_group=False):
        event_type = session.query(EventType).filter(EventType.id == type_id).first()
        user = User.create_or_get(session, line_id)
        new_event = Event(create_uid=user.id, type_id=event_type.id)
        session.add(new_event)
        session.commit()
        EventSetting.create_event_setting(session, new_event.id, is_group=is_group)
        session.refresh(new_event)
        return new_event

    @staticmethod
    def get_event(session: Session, event_id):
        event = session.query(Event).filter(Event.id == event_id).first()
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
    title = Column(String, default='未設定標題')
    description = Column(String, default='未設定敘述')
    start_time = Column(DateTime)

    @staticmethod
    def all_event_setting(session: Session, line_id, type_id=-1, is_group=False):
        user = User.create_or_get(session, line_id)
        events = session.query(Event).filter(Event.create_uid == user.id).all()
        if type_id == -1:
            events = session.query(Event).filter(Event.create_uid == user.id).all()
        else:
            session.query(Event).filter(
                Event.type_id == type_id, Event.create_uid == user.id
            ).all()
        event_settings = []
        for event in events:
            es = session.query(EventSetting) \
                .filter(EventSetting.event_id == event.id).first()
            if es is None:
                continue
            if is_group and es.is_group is False:
                continue
            event_settings.append(es)
        event_settings.reverse()
        return event_settings

    @staticmethod
    def create_event_setting(session: Session, event_id, is_group=False):
        new_event_setting = EventSetting(event_id=event_id, is_group=is_group)
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
    def update_event_setting(session: Session, event_id, title=None, description=None, start_time: datetime = None):
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

    member_id = Column(ForeignKey('user.id'), nullable=False)

    @staticmethod
    def create_or_get(session: Session, event_id, line_id):
        user = User.create_or_get(session, line_id)
        session = create_session()
        event_member = session.query(EventMember) \
            .filter(EventMember.member_id == user.id and EventMember.event_id == event_id).first()
        if event_member is None:
            event_member = EventMember(member_id=user.id, event_id=event_id)
            session.add(event_member)
            session.commit()
        return event_member

    @staticmethod
    def delete_member(session: Session, event_id, line_id) -> bool:
        user = User.create_or_get(session, line_id)
        delete_count = session.query(EventMember).filter(
            EventMember.member_id == user.id and EventMember.event_id == event_id
        ).delete()
        session.commit()
        return delete_count > 0
