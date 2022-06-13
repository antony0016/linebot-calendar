from service.todo_reply.text_message import (
    create_todo,
    db_test,
)

from service.todo_reply.postback_message import (
    create_event_by_type
)

# from

todo_replies = [
    {
        'trigger': '行事曆',
        'reply': create_todo
    },
    {
        'trigger': 'db',
        'reply': db_test
    },
]

function_mapper = {
    'todo': {
        'create': create_event_by_type,
    },
}
