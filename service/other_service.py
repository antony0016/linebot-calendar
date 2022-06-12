import os
import json
import requests


def get_weather(city):
    weather_service_token = os.getenv('WEATHER_SERVICE_TOKEN')
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + weather_service_token + '&format=JSON&locationName=' + str(
        city)
    # https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWB-0CB2B120-451C-4417-AE1E-8038A5BE654E&format=JSON&locationName=臺北市'
    data = requests.get(url)
    # return data
    # data = (json.loads(data.text,encoding='utf-8'))['records']['location'][0]['weatherElement'] #bug
    data = json.loads(data.text)
    print(data)
    # data = data['records']['location'][0]['weatherElement']
    data = data['records']['location'][0]['weatherElement']
    res = [[], [], []]
    for j in range(3):
        for i in data:
            res[j].append(i['time'][j])
    return res
