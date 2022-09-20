from sqlalchemy.orm import sessionmaker, Session
from public.instance import Base, engine


# from sqlalchemy import Column
# from sqlalchemy import DateTime
# from sqlalchemy.sql import func


def create_db():
    Base.metadata.create_all(engine)


def create_session() -> Session:
    new_session = sessionmaker(bind=engine)
    return new_session()

# class MyBase(Base):
#     create_time = Column(DateTime, server_default=func.now())
#     edit_time = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
