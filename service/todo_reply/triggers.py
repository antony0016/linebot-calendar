from service.todo_reply.text_functions import (
    create_menu,
    confirm_todo_by_text,
    create_todo,
    update_todo,
    list_all_todo,
    list_todo_option,
    db_test,
    share_event_list,
    show_code_events,
)

from service.todo_reply.postback_functions import (
    simple_reply,
    create_todo_by_text,
    event_setting_detail,
    create_event_by_type,
    update_event_by_event_id,
    list_todo_by_type_id,
    delete_event,
    list_member,
    member_join,
    member_leave,
    new_share_code,
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
        'trigger': 'Create',
        'reply': create_menu,
    },
    {
        'trigger': 'List',
        'reply': list_all_todo,
    },
    {
        'trigger': 'A',
        'reply': list_todo_option,
    },
    {
        'trigger': 'db',
        'reply': db_test
    },
    {
        'trigger': 'my-share-code',
        'reply': share_event_list,
    },
    {
        'trigger': '@code',
        'reply': show_code_events,
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
        'read': list_member,
        'create': member_join,
        'delete': member_leave,
    },
    'event_text': {
        'create': create_todo_by_text,
    },
    'menu': {
        'read': create_menu,
        # 'create': create_menu,
    },
    'share_code': {
        'create': new_share_code,
    }
    # 'a': {
    #     'show': test_func,
    # }
}
