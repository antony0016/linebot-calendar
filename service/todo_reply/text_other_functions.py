import os

import requests
from linebot.models import (
    TextSendMessage,
    TemplateSendMessage,
    CarouselTemplate, CarouselColumn,
    PostbackTemplateAction, MessageAction
)
from public.response import PostbackRequest
from constant.constants import CITIES, STAR_SIGNS, STAR_SIGN_CODE
from service.sample_reply.weather_function import current_weather


def weather_menu(event):
    request = PostbackRequest(model='weather', method='read')
    columns = []
    action = []
    for index in range(len(CITIES)):
        action.append(
            PostbackTemplateAction(
                label=CITIES[index],
                data=request.dumps(data={'city': CITIES[index]})
            )
        )
        if len(action) == 3:
            columns.append(
                CarouselColumn(
                    title='查詢天氣選單',
                    text='查詢天氣',
                    actions=action
                )
            )
            print(action)
            action = []

    return TemplateSendMessage(
        alt_text='天氣選單',
        template=CarouselTemplate(
            columns=columns
        ))


def weather_search(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    city = data['city']
    # message = event.message.text
    # if '-' not in message:
    #     return TextSendMessage(text="查詢格式為: 天氣-縣市")
    # location_args = message.replace(' ', '').split('-')
    # location_args.pop(0)
    # city = location_args[0].replace('台', '臺')
    # if city not in CITIES:
    #     return TextSendMessage(text="查無此縣市")
    # res = get_weather(city)
    response = current_weather(city)
    # print(res, res2)
    return TextSendMessage(text=response)


def star_sign_menu(event):
    request = PostbackRequest(model='star_sign', method='read')
    columns = []
    action = []
    for index in range(len(STAR_SIGNS)):
        star_sign_name = STAR_SIGNS[index]
        star_sign_code = STAR_SIGN_CODE[star_sign_name]
        action.append(
            PostbackTemplateAction(
                label=star_sign_name,
                data=request.dumps(data={'code': star_sign_code})
            )
        )
        if len(action) == 3:
            columns.append(
                CarouselColumn(
                    title='查詢星座運勢',
                    text='查詢星座',
                    actions=action
                )
            )
            print(action)
            action = []

    return TemplateSendMessage(
        alt_text='星座選單',
        template=CarouselTemplate(
            columns=columns
        ))


def get_star_sign(event):
    data = PostbackRequest(raw_data=event.postback.data).data
    star_sign_api_key = os.getenv('START_SIGN_API_KEY')
    data = requests.get(f'https://apis.tianapi.com/star/index?key={star_sign_api_key}&astro={data["code"]}')
    items = data.json()['result']['list']
    columns = []
    for item in items:
        content = item['content']
        action = {
            "label": "星座查詢選單",
            "text": 'star-sign'
        }
        if len(item['content']) > 60:
            action['label'] = '查看完整內容'
            action['text'] = content
            content = item['content'][:56] + '...'
        columns.append(
            CarouselColumn(
                title=item['type'],
                text=content,
                actions=[
                    MessageAction(
                        label=action['label'],
                        text=action['text']
                    )
                ]
            )
        )
    return TemplateSendMessage(
        alt_text='星座運勢',
        template=CarouselTemplate(
            columns=columns
        )
    )
