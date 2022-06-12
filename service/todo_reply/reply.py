from service.sample_reply.message import (
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
        'message': '最新合作廠商',
        'reply': image_map_message
    },
    {
        'message': '最新活動訊息',
        'reply': buttons_message
    },
    {
        'message': '註冊會員',
        'reply': confirm_template
    },
    {
        'message': '旋轉木馬',
        'reply': image_carousel_message1
    },
    {
        'message': '圖片畫廊',
        'reply': test_template_message
    },
    {
        'message': '功能列表',
        'reply': function_list
    },
    {
        'message': '天氣',
        'reply': weather_search
    },
]
