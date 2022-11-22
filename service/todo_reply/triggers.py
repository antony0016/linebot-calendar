from service.todo_reply.text_functions import (
    create_menu,
    create_todo_by_text,
    create_todo,
    update_todo,
    list_all_todo,
    list_todo_option,
    db_test,
    share_event_list,
    show_code_events,
    todo_edit_options,
)

from service.todo_reply.postback_functions import (
    simple_reply,
    confirm_todo_content,
    event_setting_detail,
    create_event_by_type,
    update_event_by_event_id,
    list_todo_by_type_id,
    delete_event,
    list_event_members,
    member_join,
    member_leave,
    new_share_code,
)

todo_text_replies = [
    # create event by text
    # ok
    {
        'trigger': '$',
        'reply': create_todo_by_text,
    },
    # update event by text start with @
    {
        'trigger': '@event',
        'reply': update_todo,
    },
    # create event menu
    {
        'trigger': 'Create',
        'reply': create_menu,
    },
    # menu of event search by type
    {
        'trigger': 'List',
        'reply': list_all_todo,
    },
    {
        'trigger': 'A',
        'reply': list_todo_option,
    },
    {
        'trigger': 'my-todo',
        'reply': todo_edit_options,
    },
    # show user count
    {
        'trigger': 'user',
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
    # confirm event from create_todo_by_text
    'event_text': {
        'create': confirm_todo_content,
    },
    'event': {
        'read': list_todo_option,
        'create': create_event_by_type,
        'delete': delete_event,
        'update': event_setting_detail,
        'menu': create_menu,
    },
    'event_setting': {
        'read': list_todo_by_type_id,
        'update': update_event_by_event_id,
    },
    'event_member': {
        # list event members
        # ok
        'read': list_event_members,
        # join event
        # ok
        'create': member_join,
        # leave event
        # ok
        'delete': member_leave,
    },
    'menu': {
        # create event menu
        # ok
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
