from sqlalchemy.orm import sessionmaker, Session
from public.instance import Base, engine


def create_db():
    Base.metadata.create_all(engine)


def create_session() -> Session:
    new_session = sessionmaker(bind=engine)
    return new_session()

# def create_default_data():
#     session = create_session()
#     event_type_name_list = ['event', 'todo', 'reminder']
#     for type_name in event_type_name_list:
#         event_type = session.query(EventType).filter(EventType.name == type_name).first()
#         if event_type is None:
#             event_type = EventType(name=type_name)
#             session.add(event_type)
#             session.commit()
