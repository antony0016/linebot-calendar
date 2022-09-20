import json
from typing import List

from linebot.models import CarouselColumn, MessageTemplateAction, PostbackTemplateAction
from model.todo import EventSetting


class PostbackRequest:

    def __init__(self, model='', method='', data=dict, raw_data: str = ''):
        self.model = model
        self.method = method
        self.data = data
        if raw_data != '':
            self.loads(raw_data.replace('+', ' '))

    def dumps(self, data=None) -> str:
        if data is not None:
            self.data = data
        return json.dumps(self.__dict__)

    def loads(self, raw_data: str):
        data = json.loads(raw_data)
        self.model = data['model']
        self.method = data['method']
        self.data = data['data']


def get_event_settings(event_settings: List[EventSetting]):
    columns = []
    new_data = PostbackRequest(model='event', method='update')
    delete_data = PostbackRequest(model='event', method='delete')
    for event_setting in event_settings[:10]:
        event_date = event_setting.start_time.isoformat().split('T')[0]
        event_time = event_setting.start_time.isoformat().split('T')[1]
        columns.append(CarouselColumn(
            title=str(event_setting.title),
            text='敘述：{}\n日期：{}\n時間：{}'
            .format(str(event_setting.description), event_date, event_time),
            actions=[
                PostbackTemplateAction(
                    label="細節設定",
                    data=new_data.dumps(data={'event_id': event_setting.event_id}),
                ),
                PostbackTemplateAction(
                    label="刪除",
                    data=delete_data.dumps(data={"event_id": event_setting.event_id}),
                ),
            ]
        ))
    return columns


command_text = {
    'event': """$活動$活動名稱$備註$時間""",

    'reminder': """$提醒$提醒名稱$備註$時間""",

    'todo': """$提醒$待辦事項名稱$備註$時間""",
}

normal_messages = {
    'add_event_columns': {
        'single': [
            CarouselColumn(
                title='新建提醒',
                text=command_text['reminder'],
                actions=[
                    MessageTemplateAction(
                        label='快速指令範例',
                        text='範例：$提醒$記得吃藥$$2022-09-20T09:00:00',
                    ),
                    MessageTemplateAction(
                        label='網頁建立提醒',
                        text='提醒',
                    ),
                ]
            ),
            CarouselColumn(
                title='新建代辦事項',
                text=command_text['todo'],
                actions=[
                    MessageTemplateAction(
                        label='快速指令範例',
                        text='範例：$待辦事項$繳學費$$2022-09-27T09:00:00',
                    ),
                    MessageTemplateAction(
                        label='網頁建立代辦事項',
                        text='代辦事項',
                    ),
                ]
            ),
        ],
        'group': [
            CarouselColumn(
                title='新建活動',
                text=command_text['event'],
                actions=[
                    MessageTemplateAction(
                        label='快速指令範例',
                        text='範例：$活動$週末出去玩$地點星聚點$2022-10-10T09:00:00',
                    ),
                    MessageTemplateAction(
                        label='網頁建立活動',
                        text='活動',
                    ),
                ]
            ), ],
    }
}
