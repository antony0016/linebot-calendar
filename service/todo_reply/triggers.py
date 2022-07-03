from service.todo_reply.text_functions import (
    create_todo,
    update_todo,
    list_todo,
    db_test,
)

from service.todo_reply.postback_functions import (
    create_event_by_type,
    update_event_by_event_id,
)

# from

todo_text_replies = [
    {
        'trigger': '@event',
        'reply': update_todo,
    },
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

todo_postback_replies = {
    'event': {
        'create': create_event_by_type,
    },
    'event_setting': {
        'update': update_event_by_event_id,
    },
}
