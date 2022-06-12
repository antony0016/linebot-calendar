import requests
import json
from constant.constants import WEATHER_SERVICE_TOKEN


def get_weather(city):
    weather_service_token = WEATHER_SERVICE_TOKEN
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + weather_service_token + '&format=JSON&locationName=' + str(
        city)
    # https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWB-0CB2B120-451C-4417-AE1E-8038A5BE654E&format=JSON&locationName=臺北市'
    Data = requests.get(url)
    # return Data
    # Data = (json.loads(Data.text,encoding='utf-8'))['records']['location'][0]['weatherElement'] #bug
    Data = json.loads(Data.text)
    # Data = Data['records']['location'][0]['weatherElement']
    Data = Data['records']['location'][0]['weatherElement']
    res = [[], [], []]
    for j in range(3):
        for i in Data:
            res[j].append(i['time'][j])
    return res
