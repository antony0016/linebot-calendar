from service.todo_reply.text_message import (
    create_todo,
    list_todo,
    db_test,
)

from service.todo_reply.postback_message import (
    create_event_by_type,
    update_event_by_event_id,
)

# from

todo_replies = [
    {
        'trigger': '行事曆列表',
        'reply': list_todo,
    },
    {
        'trigger': '行事曆',
        'reply': create_todo
    },
    {
        'trigger': 'db',
        'reply': db_test
    },
]

action_mapper = {
    'event': {
        'create': create_event_by_type,
    },
    'event_setting': {
        'update': update_event_by_event_id,
    },
}
