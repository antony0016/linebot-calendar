from public.instance import Base

from model.db import create_session
from model.user import User

from sqlalchemy import Column
from sqlalchemy import Integer, DateTime, String, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


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
        event_type_name_list = ['活動', '提醒', '代辦事項']
        for type_name in event_type_name_list:
            event_type = session.query(EventType).filter(EventType.name == type_name).first()
            if event_type is None:
                event_type = EventType(name=type_name)
                session.add(event_type)
                session.commit()
        session.close()

    @staticmethod
    def get_types():
        session = create_session()
        event_types = session.query(EventType).all()
        session.close()
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
    def create_event(type_id, line_id):
        session = create_session()
        event_type = session.query(EventType).filter(EventType.id == type_id).first()
        user = session.query(User).filter(User.line_id == line_id).first()
        new_event = Event(user_id=user.id, type_id=event_type.id)
        session.add(new_event)
        session.commit()
        return new_event


class EventSetting(Base):
    __tablename__ = 'event_setting'
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    event_id = Column(ForeignKey('event.id'), nullable=False, unique=True)
    event = relationship('Event', back_populates='setting')

    title = Column(String)
    description = Column(String)
    start_time = Column(DateTime)


class EventMember(Base):
    __tablename__ = 'event_member'
    id = Column(Integer, primary_key=True, autoincrement=True)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    event_id = Column(ForeignKey('event.id'), nullable=False)
    event = relationship('Event', back_populates='members')

    member_id = Column(ForeignKey('user.id'), nullable=False)
