import os
import requests
import statistics

from constant.constants import CITY_CODE

code = os.getenv('WEATHER_SERVICE_TOKEN')


# 氣象預報函式
def weather_forecast(address):
    global code
    # 將主要縣市個別的 JSON 代碼列出
    msg = '找不到天氣預報資訊。'  # 預設回傳訊息
    try:
        location_weather_raw_data = ''
        location_weather_data = dict()
        city_weather_raw_data = requests.get(
            f'https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/F-C0032-001?Authorization={code}&downloadType=WEB&format=JSON')  # 取得主要縣市預報資料
        city_weather_data_json = city_weather_raw_data.json()  # json 格式化訊息內容
        city_weather_data = city_weather_data_json['cwbopendata']['dataset']['location']  # 取得縣市的預報內容
        for data in city_weather_data:
            city = data['locationName']
            if city in address:
                weather_element = data['weatherElement']
                wx8 = weather_element[0]['time'][0]['parameter']['parameterName']  # 天氣現象
                min_temperature_8hr = weather_element[1]['time'][0]['parameter']['parameterName']  # 最低溫
                max_temperature_8hr = weather_element[2]['time'][0]['parameter']['parameterName']  # 最高溫
                # ci8 = weather_element[2]['time'][0]['parameter']['parameterName']  # 舒適度
                pop8 = weather_element[2]['time'][0]['parameter']['parameterName']  # 降雨機率
                msg = f'未來 8 小時{wx8}，最高溫 {max_temperature_8hr} 度，最低溫 {min_temperature_8hr} 度，降雨機率 {pop8} %'

                location_weather_raw_data = requests.get(
                    f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/{CITY_CODE[city]}?Authorization={code}&elementName=WeatherDescription')  # 取得主要縣市裡各個區域鄉鎮的氣象預報
                location_weather_data_json = location_weather_raw_data.json()  # json 格式化訊息內容
                location_weather_data = location_weather_data_json['records']['locations'][0]['location']  # 取得預報內容
                break

        for data in location_weather_data:
            city = data['locationName']  # 取得縣市名稱
            if city in address:  # 如果使用者的地址包含鄉鎮區域名稱
                wd = data['weatherElement'][0]['time'][1]['elementValue'][0]['value']  # 綜合描述
                msg = f'未來八小時天氣{wd}'  # 將 msg 換成對應的預報資訊
                break
        return msg  # 回傳 msg
    except Exception as e:
        print(e)
        return msg  # 如果取資料有發生錯誤，直接回傳 msg


# 目前天氣函式
def current_weather(address):
    global code
    city_list, area_list, area_list2 = {}, {}, {}  # 定義好待會要用的變數
    msg = '找不到氣象資訊。'  # 預設回傳訊息

    # 定義取得資料的函式
    def get_data(url):
        weather_raw_data = requests.get(url)  # 爬取目前天氣網址的資料
        weather_data_json = weather_raw_data.json()  # json 格式化訊息內容
        weather_data = weather_data_json['cwbopendata']['location']  # 取出對應地點的內容
        location = ''
        for data in weather_data:
            # name = info['locationName']  # 測站地點
            city = data['parameter'][0]['parameterValue']  # 城市
            area = data['parameter'][2]['parameterValue']  # 行政區
            if city in address:
                location = city
                weather_element = data['weatherElement']
                if city not in city_list:
                    city_list[city] = {'temperature': [], 'humidity': [], 'rain_24hr': []}  # 以主要縣市名稱為 key，準備紀錄裡面所有鄉鎮的數值
                temperature = check_data(weather_element[3]['elementValue']['value'])  # 氣溫
                humidity = check_data(round(float(weather_element[4]['elementValue']['value']) * 100, 1))  # 相對濕度
                rain_24hr = check_data(weather_element[6]['elementValue']['value'])  # 累積雨量
                city_list[city]['temperature'].append(temperature)  # 記錄主要縣市裡鄉鎮區域的溫度 ( 串列格式 )
                city_list[city]['humidity'].append(humidity)  # 記錄主要縣市裡鄉鎮區域的濕度 ( 串列格式 )
                city_list[city]['rain_24hr'].append(rain_24hr)  # 記錄主要縣市裡鄉鎮區域的雨量 ( 串列格式 )
                if area in address:
                    location += '-' + area
                    if area not in area_list:
                        area_list[area] = {'temperature': temperature, 'humidity': humidity,
                                           'rain_24hr': rain_24hr}  # 以鄉鎮區域為 key，儲存需要的資訊
                    # break

    # 定義如果數值小於 0，回傳 False 的函式
    def check_data(value):
        if float(value) < 0:
            return 0
        else:
            return float(value)

    # 定義產生回傳訊息的函式
    def msg_content(location_list, raw_msg):
        response = raw_msg
        print(location_list)
        for loc_name in location_list:
            if loc_name in address:  # 如果地址裡存在 key 的名稱
                temperature = f"氣溫 {location_list[loc_name]['temperature']} 度，"
                humidity = f"相對濕度 {location_list[loc_name]['humidity']}%，"
                r24 = f"累積雨量 {location_list[loc_name]['rain_24hr']}mm"
                description = f'{temperature}{humidity}{r24}'.strip('，')
                response = f'{description}。'  # 取出 key 的內容作為回傳訊息使用
                break
        return response

    try:
        # 因為目前天氣有兩組網址，兩組都爬取
        get_data(
            f'https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/O-A0001-001?Authorization={code}&downloadType=WEB&format=JSON')
        get_data(
            f'https://opendata.cwb.gov.tw/fileapi/v1/opendataapi/O-A0003-001?Authorization={code}&downloadType=WEB&format=JSON')
        city_name = ''
        for city in city_list:
            city_name = city
            if city not in area_list2:  # 將主要縣市裡的數值平均後，以主要縣市名稱為 key，再度儲存一次，如果找不到鄉鎮區域，就使用平均數值
                area_list2[city] = {
                    'temperature': round(statistics.mean(city_list[city]['temperature']), 1),
                    'humidity': round(statistics.mean(city_list[city]['humidity']), 1),
                    'rain_24hr': round(statistics.mean(city_list[city]['rain_24hr']), 1)
                }
        msg = msg_content(area_list2, msg)  # 將訊息改為「大縣市」
        # msg = msg_content(area_list, msg)  # 將訊息改為「鄉鎮區域」
        return f'{city_name} {msg}'  # 回傳 msg
    except Exception as e:
        print(e)
        return msg  # 如果取資料有發生錯誤，直接回傳 msg

# 空氣品質函式
# def aqi(address):
#     city_list, site_list = {}, {}
#     msg = '找不到空氣品質資訊。'
#     try:
#         url = f'https://data.epa.gov.tw/api/v1/aqx_p_432?limit=1000&api_key={code}&sort=ImportDate%20desc&format=json'
#         a_data = requests.get(url)  # 使用 get 方法透過空氣品質指標 API 取得內容
#         a_data_json = a_data.json()  # json 格式化訊息內容
#         for i in a_data_json['records']:  # 依序取出 records 內容的每個項目
#             city = i['County']  # 取出縣市名稱
#             if city not in city_list:
#                 city_list[city] = []  # 以縣市名稱為 key，準備存入串列資料
#             site = i['SiteName']  # 取出鄉鎮區域名稱
#             aqi = int(i['AQI'])  # 取得 AQI 數值
#             status = i['Status']  # 取得空氣品質狀態
#             site_list[site] = {'aqi': aqi, 'status': status}  # 記錄鄉鎮區域空氣品質
#             city_list[city].append(aqi)  # 將各個縣市裡的鄉鎮區域空氣 aqi 數值，以串列方式放入縣市名稱的變數裡
#         for i in city_list:
#             if i in address:  # 如果地址裡包含縣市名稱的 key，就直接使用對應的內容
#                 # https://airtw.epa.gov.tw/cht/Information/Standard/AirQualityIndicator.aspx
#                 aqi_val = round(statistics.mean(city_list[i]), 0)  # 計算平均數值，如果找不到鄉鎮區域，就使用縣市的平均值
#                 aqi_status = ''  # 手動判斷對應的空氣品質說明文字
#                 if aqi_val <= 50:
#                     aqi_status = '良好'
#                 elif 50 < aqi_val <= 100:
#                     aqi_status = '普通'
#                 elif 100 < aqi_val <= 150:
#                     aqi_status = '對敏感族群不健康'
#                 elif 150 < aqi_val <= 200:
#                     aqi_status = '對所有族群不健康'
#                 elif 200 < aqi_val <= 300:
#                     aqi_status = '非常不健康'
#                 else:
#                     aqi_status = '危害'
#                 msg = f'空氣品質{aqi_status} ( AQI {aqi_val} )。'  # 定義回傳的訊息
#                 break
#         for i in site_list:
#             if i in address:  # 如果地址裡包含鄉鎮區域名稱的 key，就直接使用對應的內容
#                 msg = f'空氣品質{site_list[i]["status"]} ( AQI {site_list[i]["aqi"]} )。'
#                 break
#         return msg  # 回傳 msg
#     except Exception as e:
#         print(e)
#         return msg  # 如果取資料有發生錯誤，直接回傳 msg
#
#
# # 地震資訊函式
# def earth_quake():
#     global code
#     msg = ['找不到地震資訊', 'https://example.com/demo.jpg']
#     try:
#         url = f'https://opendata.cwb.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={code}'
#         e_data = requests.get(url)  # 爬取地震資訊網址
#         e_data_json = e_data.json()  # json 格式化訊息內容
#         eq = e_data_json['records']['earthquake']  # 取出地震資訊
#         for i in eq:
#             loc = i['earthquakeInfo']['epiCenter']['location']  # 地震地點
#             val = i['earthquakeInfo']['magnitude']['magnitudeValue']  # 地震規模
#             dep = i['earthquakeInfo']['depth']['value']  # 地震深度
#             eq_time = i['earthquakeInfo']['originTime']  # 地震時間
#             img = i['reportImageURI']  # 地震圖
#             msg = [f'{loc}，芮氏規模 {val} 級，深度 {dep} 公里，發生時間 {eq_time}。', img]
#             break  # 取出第一筆資料後就 break
#         return msg  # 回傳 msg
#     except Exception as e:
#         print(e)
#         return msg  # 如果取資料有發生錯誤，直接回傳 msg
