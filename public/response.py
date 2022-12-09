import json
from typing import List

from linebot.models import (
    CarouselColumn, MessageTemplateAction, PostbackTemplateAction, URITemplateAction,
    QuickReplyButton, QuickReply, TextSendMessage, TemplateSendMessage, CarouselTemplate,
)

from model.response import PostbackRequest
from model.todo import EventSetting


def show_event_members_action(event_setting: EventSetting):
    request = PostbackRequest(model='event', method='show_members', )
    return PostbackTemplateAction(
        label='查看成員',
        data=request.dumps(data={'event_id': event_setting.event_id})
    )


def get_event_details(event_settings: List[EventSetting], is_group=False):
    columns = []
    for event_setting in event_settings[:10]:
        actions = []
        # if is_group:
        # actions.append(show_event_members_action(event_setting))
        print(event_setting.start_time)
        columns.append(
            event_setting.to_line_template(is_column=True, custom_actions=actions)
        )
    return columns


command_text = {
    'event': """$活動$活動名稱$備註$時間""",
    'reminder': """$提醒$提醒名稱$備註$時間""",
    'todo': """$待辦事項$待辦事項名稱""",
}


def get_quick_reply(event_id=None):
    request = PostbackRequest(model='event', data={'event_id': event_id})
    quick_reply_attr = [
        {'method': 'read', 'label': '查詢行事曆'},
        {'method': 'update', 'label': '行事曆細節設定'},
        {'method': 'delete', 'label': '刪除行事曆'},
    ]
    quick_reply_actions = []
    for attr in quick_reply_attr:
        quick_reply_actions.append(
            QuickReplyButton(
                action=PostbackTemplateAction(
                    label=attr['label'],
                    data=request.dumps(method=attr['method'])
                )
            )
        )
        if event_id is None:
            break
    return quick_reply_actions


def get_default_message(group_id=None):
    if group_id is None:
        return [
            CarouselColumn(
                title='新建提醒',
                text=command_text['reminder'],
                actions=[
                    MessageTemplateAction(
                        label='快速指令範例',
                        text='範例：$提醒$記得吃藥$藥放在櫃子裡$2022-09-20T09:00:00',
                    ),
                    URITemplateAction(
                        label='網頁建立提醒',
                        uri='https://liff.line.me/1657271223-veVzj6al?typeID=2',
                    ),
                ]
            ),
            CarouselColumn(
                title='新建待辦事項',
                text=command_text['todo'],
                actions=[
                    MessageTemplateAction(
                        label='快速指令範例',
                        text='範例：$待辦事項$繳學費',
                    ),
                    URITemplateAction(
                        label='網頁建立待辦事項',
                        uri='https://liff.line.me/1657271223-veVzj6al?typeID=3',
                    ),
                ]
            ),
        ]
    return [
        CarouselColumn(
            title='新建活動',
            text=command_text['event'],
            actions=[
                MessageTemplateAction(
                    label='快速指令範例',
                    text='範例：$活動$週末出去玩$地點星聚點$2022-10-10T09:00:00',
                ),
                URITemplateAction(
                    label='網頁建立活動',
                    uri=f'https://liff.line.me/1657271223-veVzj6al?typeID=1&group_id={group_id}',
                ),
            ]
        ),
        CarouselColumn(
            title='新建待辦事項',
            text=command_text['todo'],
            actions=[
                MessageTemplateAction(
                    label='快速指令範例',
                    text='範例：$待辦事項$繳學費',
                ),
                URITemplateAction(
                    label='網頁建立待辦事項',
                    uri=f'https://liff.line.me/1657271223-veVzj6al?typeID=3&group_id={group_id}',
                ),
            ]
        ),
    ]
