from service.todo_reply.text_message import (
    create_todo,
    db_test,
)

# from

todo_replies = [
    {
        'message': '行事曆',
        'reply': create_todo
    },
    {
        'message': 'db',
        'reply': db_test
    },
]

function_mapper = {
    'todo': {
        'create': '',
    },
}
