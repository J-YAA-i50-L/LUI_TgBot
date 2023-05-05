import json
import requests as req

latitude = 55.75396
longitude = 37.620393


def yandex_weather(latitude, longitude):
    url_yandex = f'https://api.weather.yandex.ru/v2/forecast/?lat={latitude}&lon={longitude}&[lang=ru_RU]&limit1'
    yandex_req = req.get(url_yandex, headers={'X-Yandex-API-Key': '7e7676aa-ce54-46b2-83d3-e0f46b9a7a5b'})
    conditions = {'clear': 'ясно', 'partly-cloudy': 'малооблачно', 'cloudy': 'облачно с прояснениями',
                  'overcast': 'пасмурно', 'drizzle': 'морось', 'light-rain': 'небольшой дождь',
                  'rain': 'дождь', 'moderate-rain': 'умеренно сильный', 'heavy-rain': 'сильный дождь',
                  'continuous-heavy-rain': 'длительный сильный дождь', 'showers': 'ливень',
                  'wet-snow': 'дождь со снегом', 'light-snow': 'небольшой снег', 'snow': 'снег',
                  'snow-showers': 'снегопад', 'hail': 'град', 'thunderstorm': 'гроза',
                  'thunderstorm-with-rain': 'дождь с грозой', 'thunderstorm-with-hail': 'гроза с градом'
                  }
    wind_dir = {'nw': 'северо-западное', 'n': 'северное', 'ne': 'северо-восточное', 'e': 'восточное',
                'se': 'юго-восточное', 's': 'южное', 'sw': 'юго-западное', 'w': 'западное', 'с': 'штиль'}
    yandex_json = json.loads(yandex_req.text)
    json_fact = yandex_json["fact"]
    temp = json_fact["temp"]
    feels_like = json_fact['feels_like']

    weater = f'Сейчас температура на улице равна {temp}, но ощущается как {feels_like}' \
             f'Погода {}.' \
             f'Скорость ветра  {}, направление {}.'
    return weater




print(yandex_weather(latitude,longitude))