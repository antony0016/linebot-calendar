from public.instance import Base

from sqlalchemy import Column
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session import Session


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(String, nullable=False)
    create_time = Column(DateTime, server_default=func.now())
    edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())

    events = relationship('Event', back_populates='create_user')

    @staticmethod
    def create_or_get(session: Session, line_id):
        user = session.query(User).filter(User.line_id == line_id).first()
        if user is None:
            user = User(line_id=line_id)
            session.add(user)
            session.commit()
        return user
