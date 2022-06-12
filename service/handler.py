from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import TextMessage, MessageEvent
from messages.other_service import get_weather

from constant.constants import CITIES


# 處理訊息
def text_message_handler(event) -> dict:
    msg = event.message.text
    reply_message = None
    if True:
        if '最新合作廠商' in msg:
            message = imagemap_message()
            reply_message = message
        elif '最新活動訊息' in msg:
            message = buttons_message()
            reply_message = message
            line_bot_api.reply_message(event.reply_token, message)
        elif '註冊會員' in msg:
            message = Confirm_Template()
            reply_message = message
        elif '旋轉木馬' in msg:
            message = Carousel_Template()
            reply_message = message
        elif '圖片畫廊' in msg:
            message = test()
            reply_message = message
        elif '功能列表' in msg:
            message = function_list()
            reply_message = message

        elif '貓咪大戰爭' in msg:
            message = TextSendMessage(text=f'傻眼貓咪')
            reply_message = message

        elif '早安' in msg:
            message = TextSendMessage(text=f'芊慧趕快起床要去上班了!')
            reply_message = message

        elif '下班了' in msg:
            message = TextSendMessage(text=f'611公車再3分鐘即將進站')
            reply_message = message

        elif '家裡有晚餐嗎' in msg:
            message = TextSendMessage(text=f'媽媽有煮一大鍋牛肉麵在廚房等妳趕快回來吃!')
            reply_message = message

        elif '家裡有晚餐嗎?' in msg:
            message = TextSendMessage(text=f'媽媽有煮一大鍋牛肉麵在廚房等妳趕快回來吃!')
            reply_message = message

        elif '好的' in msg:
            message = TextSendMessage(text=f'那等會見，已幫妳準備好餐具和茶杯放桌上。')
            reply_message = message

        elif '我愛你' in msg:
            message = TextSendMessage(text=f'我也愛你')
            reply_message = message

        elif '老公早安' in msg:
            message = TextSendMessage(text=f'老婆早安')
            reply_message = message

        elif '老公晚安' in msg:
            message = TextSendMessage(text=f'老婆晚安')
            reply_message = message

        elif '誰是大美女' in msg:
            message = TextSendMessage(text=f'是宋芊慧')
            reply_message = message

        elif '提摩西' in msg:
            message = TextSendMessage(text="https://www.instagram.com/tchalamet")
            reply_message = message
        elif '我的男神ig' in msg:
            message = TextSendMessage(text="https://www.instagram.com/tchalamet")
            reply_message = message
        else:
            # message = TextSendMessage(text=msg)
            # line_bot_api.reply_message(event.reply_token, message)
            if (msg[:2] == '天氣'):
                city = msg[3:]
                city = city.replace('台', '臺')
                if (not (city in CITIES)):
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="查詢格式為: 天氣 縣市"))
                else:
                    res = getWeather(city)
                    # line_bot_api.reply_message(event.reply_token,TextSendMessage(text="123"))
                    line_bot_api.reply_message(event.reply_token, TemplateSendMessage(
                        alt_text=city + '未來 36 小時天氣預測',
                        template=CarouselTemplate(
                            columns=[
                                CarouselColumn(
                                    thumbnail_image_url='https://i.imgur.com/Ex3Opfo.png',
                                    title='{} ~ {}'.format(res[0][0]['startTime'][5:-3], res[0][0]['endTime'][5:-3]),
                                    text='天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(data[0]['parameter']['parameterName'],
                                                                                  data[2]['parameter']['parameterName'],
                                                                                  data[4]['parameter']['parameterName'],
                                                                                  data[1]['parameter'][
                                                                                      'parameterName']),
                                    actions=[
                                        URIAction(
                                            label='詳細內容',
                                            uri='https://www.cwb.gov.tw/V8/C/W/County/index.html'
                                        )
                                    ]
                                ) for data in res
                            ]
                        )
                    ))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

    return {
        'reply_token': event.reply_token,
        'message': reply_message
    }


def postback_message_handler(event) -> dict:
    data = event.postback.data
    reply_message = None

    return {
        'reply_token': event.reply_token,
        'message': reply_message
    }
