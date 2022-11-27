from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from service.other_service import get_weather
from service.sample_reply.weather_function import current_weather
from constant.constants import CITIES
from linebot.models import (
    # message
    TextSendMessage,
    ImagemapSendMessage,
    TemplateSendMessage,

    # template
    ButtonsTemplate,
    ConfirmTemplate,
    PostbackTemplateAction,
    ImageCarouselTemplate,
    ImageCarouselColumn,
    CarouselTemplate,
    CarouselColumn,

    # action
    URIImagemapAction,
    DatetimePickerTemplateAction,
    MessageTemplateAction,
    URITemplateAction,
    URIAction,

    # others
    ImagemapArea,
    BaseSize,
)


# ImageMapSendMessage(組圖訊息)
def image_map_message(event):
    return ImagemapSendMessage(
        base_url="https://i.imgur.com/BfTFVDN.jpg",
        alt_text='最新的合作廠商有誰呢？',
        base_size=BaseSize(height=2000, width=2000),
        actions=[
            URIImagemapAction(
                # 家樂福
                link_uri="https://tw.shop.com/search/%E5%AE%B6%E6%A8%82%E7%A6%8F",
                area=ImagemapArea(
                    x=0, y=0, width=1000, height=1000
                )
            ),
            URIImagemapAction(
                # 生活市集
                link_uri="https://tw.shop.com/search/%E7%94%9F%E6%B4%BB%E5%B8%82%E9%9B%86",
                area=ImagemapArea(
                    x=1000, y=0, width=1000, height=1000
                )
            ),
            URIImagemapAction(
                # 阿瘦皮鞋
                link_uri="https://tw.shop.com/search/%E9%98%BF%E7%98%A6%E7%9A%AE%E9%9E%8B",
                area=ImagemapArea(
                    x=0, y=1000, width=1000, height=1000
                )
            ),
            URIImagemapAction(
                # 塔吉特千層蛋糕
                link_uri="https://tw.shop.com/search/%E5%A1%94%E5%90%89%E7%89%B9",
                area=ImagemapArea(
                    x=1000, y=1000, width=1000, height=500
                )
            ),
            #            URIImagemapAction(
            #                #亞尼克生乳捲
            #                link_uri="https://tw.shop.com/search/%E4%BA%9E%E5%B0%BC%E5%85%8B",
            #                area=ImagemapArea(
            #                    x=1000, y=1500, width=1000, height=500
            #                )
            #            ),
            URIImagemapAction(
                # 提摩西·夏勒梅
                link_uri="https://zh.wikipedia.org/zh-tw/%E6%8F%90%E6%91%A9%E8%A5%BF%C2%B7%E5%A4%8F%E5%8B%92%E6%A2%85",
                area=ImagemapArea(
                    x=1000, y=1500, width=1000, height=500
                )
            )

        ]
    )


# TemplateSendMessage - ButtonsTemplate (按鈕介面訊息)
def buttons_message(event):
    return TemplateSendMessage(
        alt_text='好消息來囉～',
        template=ButtonsTemplate(
            thumbnail_image_url="https://pic2.zhimg.com/v2-de4b8114e8408d5265503c8b41f59f85_b.jpg",
            title="是否要進行抽獎活動？",
            text="輸入生日後即獲得抽獎機會",
            actions=[
                DatetimePickerTemplateAction(
                    label="請選擇生日",
                    data="input_birthday",
                    mode='date',
                    initial='1990-01-01',
                    max='2019-03-10',
                    min='1930-01-01'
                ),
                MessageTemplateAction(
                    label="看抽獎品項",
                    text="有哪些抽獎品項呢？"
                ),
                URITemplateAction(
                    label="免費註冊享回饋",
                    uri="https://tw.shop.com/nbts/create-myaccount.xhtml?returnurl=https%3A%2F%2Ftw.shop.com%2F"
                )
            ]
        )
    )


# TemplateSendMessage - ConfirmTemplate(確認介面訊息)
def confirm_template(event):
    return TemplateSendMessage(
        alt_text='是否註冊成為會員？',
        template=ConfirmTemplate(
            text="是否註冊成為會員？",
            actions=[
                PostbackTemplateAction(
                    label="馬上註冊",
                    text="現在、立刻、馬上",
                    data="會員註冊"
                ),
                MessageTemplateAction(
                    label="查詢其他功能",
                    text="查詢其他功能"
                )
            ]
        )
    )


# 旋轉木馬按鈕訊息介面
def carousel_template(event):
    return TemplateSendMessage(
        alt_text='一則旋轉木馬按鈕訊息',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Number_1_in_green_rounded_square.svg/200px-Number_1_in_green_rounded_square.svg.png',
                    title='這是第一塊模板',
                    text='一個模板可以有三個按鈕',
                    actions=[
                        PostbackTemplateAction(
                            label='回傳一個訊息',
                            data='將這個訊息偷偷回傳給機器人'
                        ),
                        MessageTemplateAction(
                            label='用戶發送訊息',
                            text='我知道這是1'
                        ),
                        URITemplateAction(
                            label='進入1的網頁',
                            uri='https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Number_1_in_green_rounded_square.svg/200px-Number_1_in_green_rounded_square.svg.png'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRuo7n2_HNSFuT3T7Z9PUZmn1SDM6G6-iXfRC3FxdGTj7X1Wr0RzA',
                    title='這是第二塊模板',
                    text='副標題可以自己改',
                    actions=[
                        PostbackTemplateAction(
                            label='回傳一個訊息',
                            data='這是ID=2'
                        ),
                        MessageTemplateAction(
                            label='用戶發送訊息',
                            text='我知道這是2'
                        ),
                        URITemplateAction(
                            label='進入2的網頁',
                            uri='https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Number_2_in_light_blue_rounded_square.svg/200px-Number_2_in_light_blue_rounded_square.svg.png'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Number_3_in_yellow_rounded_square.svg/200px-Number_3_in_yellow_rounded_square.svg.png',
                    title='這是第三個模塊',
                    text='最多可以放十個',
                    actions=[
                        PostbackTemplateAction(
                            label='回傳一個訊息',
                            data='這是ID=3'
                        ),
                        MessageTemplateAction(
                            label='用戶發送訊息',
                            text='我知道這是3'
                        ),
                        URITemplateAction(
                            label='uri2',
                            uri='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Number_3_in_yellow_rounded_square.svg/200px-Number_3_in_yellow_rounded_square.svg.png'
                        )
                    ]
                )
            ]
        )
    )


# TemplateSendMessage - ImageCarouselTemplate(圖片旋轉木馬)
def image_carousel_message1(event):
    return TemplateSendMessage(
        alt_text='圖片旋轉木馬',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/uKYgfVs.jpg",
                    action=URITemplateAction(
                        label="新鮮水果",
                        uri="http://img.juimg.com/tuku/yulantu/110709/222-110F91G31375.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QOcAvjt.jpg",
                    action=URITemplateAction(
                        label="新鮮蔬菜",
                        uri="https://cdn.101mediaimage.com/img/file/1410464751urhp5.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/Np7eFyj.jpg",
                    action=URITemplateAction(
                        label="可愛狗狗",
                        uri="http://imgm.cnmo-img.com.cn/appimg/screenpic/big/674/673928.JPG"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QRIa5Dz.jpg",
                    action=URITemplateAction(
                        label="可愛貓咪",
                        uri="https://m-miya.net/wp-content/uploads/2014/07/0-065-1.min_.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/Np7eFyj.jpg",
                    action=URITemplateAction(
                        label="可愛巧虎島",
                        uri="http://imgm.cnmo-img.com.cn/appimg/screenpic/big/674/673928.JPG"
                    )
                )
            ]
        )
    )


# test_template_message
def test_template_message(event):
    return TemplateSendMessage(
        alt_text='圖片旋轉木馬',
        template=ImageCarouselTemplate(
            columns=[
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/uKYgfVs.jpg",
                    action=URITemplateAction(
                        label="新鮮水果",
                        uri="http://img.juimg.com/tuku/yulantu/110709/222-110F91G31375.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QOcAvjt.jpg",
                    action=URITemplateAction(
                        label="新鮮蔬菜",
                        uri="https://cdn.101mediaimage.com/img/file/1410464751urhp5.jpg"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/Np7eFyj.jpg",
                    action=URITemplateAction(
                        label="可愛狗狗",
                        uri="http://imgm.cnmo-img.com.cn/appimg/screenpic/big/674/673928.JPG"
                    )
                ),
                ImageCarouselColumn(
                    image_url="https://i.imgur.com/QRIa5Dz.jpg",
                    action=URITemplateAction(
                        label="可愛貓咪",
                        uri="https://m-miya.net/wp-content/uploads/2014/07/0-065-1.min_.jpg"
                    )
                )
            ]
        )
    )


# 功能列表
def function_list(event):
    return TemplateSendMessage(
        alt_text='功能列表',
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQkl5qgGtBxZbBu921rynn7HN7C7JaD_Hbi5cMMV5gEgQu2mE-rIw',
                    title='Maso萬事屋百貨',
                    text='百萬種商品一站購足',
                    actions=[
                        MessageTemplateAction(
                            label='關於Maso百貨',
                            text='Maso萬事屋百貨是什麼呢？'
                        ),
                        URITemplateAction(
                            label='點我逛百貨',
                            uri='https://tw.shop.com/maso0310'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://www.youtaker.com/video2015/promo/images/promo-vip.png',
                    title='註冊成為會員',
                    text='免費獲得會員好康！',
                    actions=[
                        MessageTemplateAction(
                            label='會員優惠資訊',
                            text='我想瞭解註冊會員的好處是什麼'
                        ),
                        URITemplateAction(
                            label='點我註冊會員',
                            uri='https://tw.shop.com/nbts/create-myaccount.xhtml?returnurl=https%3A%2F%2Ftw.shop.com%2F'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://img.shop.com/Image/Images/11module/MABrands/opc3Chews_usa_32979_LogoTreatment_200x75.svg',
                    title='獨家商品',
                    text='百種優質獨家商品',
                    actions=[
                        MessageTemplateAction(
                            label='點我看產品目錄',
                            text='獨家商品有哪些？'
                        ),
                        URITemplateAction(
                            label='購買獨家品牌',
                            uri='https://tw.shop.com/info/our-brands'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://img.shop.com/Image/featuredhotdeal/GOMAJI1551245496503.jpg',
                    title='優惠資訊',
                    text='隨時更新最新優惠',
                    actions=[
                        MessageTemplateAction(
                            label='抽一個優惠',
                            text='抽優惠資訊'
                        ),
                        URITemplateAction(
                            label='近期優惠資訊',
                            uri='https://tw.shop.com/hot-deals'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://img.shop.com/Image/featuredhotdeal/Carrefour1551245288925.jpg',
                    title='最新消息',
                    text='最新活動訊息',
                    actions=[
                        MessageTemplateAction(
                            label='點我看最新消息',
                            text='我想瞭解最新活動'
                        ),
                        URITemplateAction(
                            label='活動資訊頁面',
                            uri='https://tw.shop.com/hot-deals'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://img.technews.tw/wp-content/uploads/2014/05/TechNews-624x482.jpg',
                    title='每日新知',
                    text='定期更新相關資訊',
                    actions=[
                        MessageTemplateAction(
                            label='點我看每日新知',
                            text='抽一則每日新知'
                        ),
                        URITemplateAction(
                            label='更多更新內容',
                            uri='https://www.youtube.com/channel/UCpzVAEwEs9AwT2uAOZuxaRQ?view_as=subscriber'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://www.wecooperation.com/makemoney/%E7%9F%A5%E5%90%8D%E5%A4%A5%E4%BC%B4%E5%95%86%E5%BA%97.png',
                    title='好店分享',
                    text='優質商品介紹與分享',
                    actions=[
                        MessageTemplateAction(
                            label='夥伴商店推薦',
                            text='抽一家夥伴商店'
                        ),
                        URITemplateAction(
                            label='查詢夥伴商店',
                            uri='https://tw.shop.com/stores-a-z'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://img.shop.com/Image/Images/landingPages/ps-recruit/twn-ps-recruit-header.jpg',
                    title='招商說明',
                    text='與Shop.com合作',
                    actions=[
                        MessageTemplateAction(
                            label='招商資訊',
                            text='如何成為夥伴商店'
                        ),
                        URITemplateAction(
                            label='招商說明報名頁面',
                            uri='https://tw.shop.com/ps_recruit_intro-v.xhtml?tkr=180530162209'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://images.marketamerica.com/site/br/images/logos/awards/torch-award-ethics-2018.jpg',
                    title='微型創業資訊',
                    text='加入網路微型創業趨勢',
                    actions=[
                        MessageTemplateAction(
                            label='瞭解更多',
                            text='什麼是微型創業資訊'
                        ),
                        URITemplateAction(
                            label='公司簡介',
                            uri='https://www.marketamerica.com/?localeCode=zh-Hant&redirect=true'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://scontent-sjc3-1.xx.fbcdn.net/v/t1.0-1/p320x320/50934385_2553136691368417_7766092240367124480_n.jpg?_nc_cat=109&_nc_ht=scontent-sjc3-1.xx&oh=c144a6b45450781ccaf258beb40bc53e&oe=5D228BF1',
                    title='聯繫Maso本人',
                    text='直接聯繫Maso',
                    actions=[
                        MessageTemplateAction(
                            label='誰是Maso?',
                            text='Maso是誰？想認識'
                        ),
                        URITemplateAction(
                            label='加我的LINE',
                            uri='https://line.me/ti/p/KeRocPY6PP'
                        )
                    ]
                )
            ]
        )
    )


# 天氣
def weather_search(event):
    message = event.message.text
    if '-' not in message:
        return TextSendMessage(text="查詢格式為: 天氣-縣市")
    location_args = message.replace(' ', '').split('-')
    location_args.pop(0)
    city = location_args[0].replace('台', '臺')
    area = ''
    if len(location_args) > 1:
        area = location_args[1].replace('台', '臺')
    if city not in CITIES:
        return TextSendMessage(text="查無此縣市")
    # res = get_weather(city)
    res2 = current_weather(city + area)
    # print(res, res2)
    return TextSendMessage(text=res2)
    # return TemplateSendMessage(
    #     alt_text=city + '未來 36 小時天氣預測',
    #     template=CarouselTemplate(
    #         columns=[
    #             CarouselColumn(
    #                 thumbnail_image_url='https://i.imgur.com/Ex3Opfo.png',
    #                 title='{} ~ {}'.format(res[0][0]['startTime'][5:-3], res[0][0]['endTime'][5:-3]),
    #                 text='天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(
    #                     data[0]['parameter']['parameterName'], data[2]['parameter']['parameterName'],
    #                     data[4]['parameter']['parameterName'], data[1]['parameter']['parameterName']
    #                 ),
    #                 actions=[
    #                     URIAction(
    #                         label='詳細天氣資訊',
    #                         uri='https://www.cwb.gov.tw/V8/C/W/County/index.html'
    #                     )
    #                 ]
    #             ) for data in res
    #         ]
    #     )
    # )
