from public.instance import Base

from sqlalchemy import Column
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session
from public.instance import line_bot_api


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(String, nullable=False)
    name = Column(String, default='找不到用戶名字')
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    events = relationship('Event', back_populates='create_user')
    member = relationship('EventMember', back_populates='user')
    shared_codes = relationship('ShareCode', back_populates='share_user')

    # share_records = relationship('ShareRecord', back_populates='user')

    @staticmethod
    def create_or_get(session: Session, line_id):
        user = session.query(User).filter(User.line_id == line_id).first()
        if user is None:
            user_profile = line_bot_api.get_profile(user_id=line_id)
            user = User(line_id=line_id, name=user_profile.display_name)
            session.add(user)
            session.commit()
        return user
