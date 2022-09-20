from service.todo_reply.text_functions import (
    create_menu,
    confirm_todo_by_text,
    create_todo,
    update_todo,
    list_todo,
    list_todo_option,
    db_test,
)

from service.todo_reply.postback_functions import (
    simple_reply,
    create_todo_by_text,
    event_setting_detail,
    create_event_by_type,
    update_event_by_event_id,
    list_todo_by_type_id,
    delete_event,
    member_join,
    member_leave,
)

# from

todo_text_replies = [
    {
        'trigger': '$',
        'reply': confirm_todo_by_text,
    },
    {
        'trigger': '@event',
        'reply': update_todo,
    },
    {
        'trigger': '建立行事曆',
        'reply': create_menu,
    },
    {
        'trigger': '行事曆列表',
        'reply': list_todo,
    },
    {
        'trigger': 'A',
        'reply': list_todo_option,
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
    'reply': {
        'create': simple_reply,
    },
    'event': {
        'read': list_todo_option,
        'create': create_event_by_type,
        'delete': delete_event,
        'update': event_setting_detail,
    },
    'event_setting': {
        'read': list_todo_by_type_id,
        'update': update_event_by_event_id,
    },
    'event_member': {
        'create': member_join,
        'delete': member_leave,
    },
    'event_text': {
        'create': create_todo_by_text,
    },
    'menu': {
        'create': create_menu,
    },
    'a':{
        'show': test_func,
    }
}
