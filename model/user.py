from public.instance import Base

from model.db import create_session

from sqlalchemy import Column
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(String, nullable=False)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    events = relationship('Event', back_populates='create_user')

    @staticmethod
    def create_or_get(line_id):
        session = create_session()
        user = session.query(User).filter(User.line_id == line_id).first()
        if user is None:
            user = User(line_id=line_id)
            session.add(user)
            session.commit()
        session.close()
        return user
