from service.sample_reply.text_functions import (
    image_map_message,
    buttons_message,
    confirm_template,
    test_template_message,
    image_carousel_message1,
    function_list,

    weather_search,
)

sample_replies = [
    {
        'trigger': '資訊',
        'reply': image_map_message
    },
    {
        'trigger': '最新合作廠商',
        'reply': image_map_message
    },
    {
        'trigger': '最新活動訊息',
        'reply': buttons_message
    },
    {
        'trigger': '註冊會員',
        'reply': confirm_template
    },
    {
        'trigger': '旋轉木馬',
        'reply': image_carousel_message1
    },
    {
        'trigger': '圖片畫廊',
        'reply': test_template_message
    },
    {
        'trigger': '功能列表',
        'reply': function_list
    },
    {
        'trigger': '天氣',
        'reply': weather_search
    },
]
