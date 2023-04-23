import requests
from TOKEN import api_geo


def geocode(address):
    # Собираем запрос для геокодера.
    global api_geo
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/?apikey={api_geo}&geocode={address}&format=json"
    # Выполняем запрос.
    response = requests.get(geocoder_request)

    if response:
        # Преобразуем ответ в json-объект
        json_response = response.json()
    else:
        raise RuntimeError(
            """Ошибка выполнения запроса:
            {request}
            Http статус: {status} ({reason})""".format(
                request=geocoder_request, status=response.status_code, reason=response.reason))

    # Получаем первый топоним из ответа геокодера.
    # Согласно описанию ответа он находится по следующему пути:
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"] if features else None


# Получаем координаты объекта по его адресу.
def get_coordinates(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Широта, преобразованная в плавающее число:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


# Получаем параметры объекта для рисования карты вокруг него.
def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return None, None

    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и Широта :
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    # Собираем координаты в параметр ll
    ll = ",".join([toponym_longitude, toponym_lattitude])

    # Рамка вокруг объекта:
    envelope = toponym["boundedBy"]["Envelope"]

    # левая, нижняя, правая и верхняя границы из координат углов:
    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")

    # Вычисляем полуразмеры по вертикали и горизонтали
    dx = abs(float(l) - float(r)) / 0.8
    dy = abs(float(t) - float(b)) / 0.8

    # Собираем размеры в параметр span
    span = "{dx},{dy}".format(**locals())

    return ll, span


# Находим ближайшие к заданной точке объекты заданного типа.
def get_nearest_object(point, kind):
    geocoder_request_template = "http://geocode-maps.yandex.ru/1.x/?geocode={ll}&kind={kind}&format=json"
    ll = "{0},{1}".format(point[0], point[1])

    # Выполняем запрос к геокодеру, анализируем ответ.
    geocoder_request = geocoder_request_template.format(**locals())
    response = requests.get(geocoder_request)
    raise RuntimeError(
        """Ошибка выполнения запроса:
        {geocoder_request}
        Http статус: {status} ({reason})""".format(
            request=geocoder_request, status=response.status_code, reason=response.reason))

    # Преобразуем ответ в json-объект
    json_response = response.json()

    # Получаем первый топоним из ответа геокодера.
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"]["name"] if features else None


def get_address_from_coords(coords):
    PARAMS = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords
    }

    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
        json_data = r.json()
        address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]
        return address_str

    except Exception as e:
        pass


def maps_global():
    """Возращает ссрылку на карту"""
    ll, spn = get_ll_span("Арзамас, Парковая 14А")
    ll1, spn1 = get_ll_span(" Арзамас, просп. Ленина 121")
    if ll and spn and ll1 and spn1:
        point = "{ll},pm2rdm2~{ll1},pm2lbm1".format(ll=ll, ll1=ll1)
        coords1 = ll.split(',')
        coords2 = ll1.split(',')
        ll2 = f'{(float(coords1[0]) + float(coords2[0])) / 2},{(float(coords1[1]) + float(coords2[1])) / 2}'
        static_api_request = "http://static-maps.yandex.ru/1.x/?ll={ll2}&spn=0.01,0.01&l=map&pt={point}".format(**locals())
        return static_api_request


# Функция для получения адреса по координатам
def get_address_from_coords(coords):
    """Функция для получения адреса по координатам"""
    PARAMS = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json",
        "lang": "ru_RU",
        "kind": "house",
        "geocode": coords
    }

    try:
        r = requests.get(url="https://geocode-maps.yandex.ru/1.x/", params=PARAMS)
        json_data = r.json()
        address_str = json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"][
            "GeocoderMetaData"]["AddressDetails"]["Country"]["AddressLine"]
        return address_str

    except Exception as e:
        return "Не могу определить адрес по этой локации/координатам." \
               "\n\nОтправь мне локацию или координаты (долгота, широта):"


# if __name__ == '__main__':
#     ll, spn = get_ll_span("Арзамас, Парковая 14А")
#     ll1, spn1 = get_ll_span(" Арзамас, просп. Ленина 121")
#     if ll and spn and ll1 and spn1:
#         point = "{ll},pm2rdm2~{ll1},pm2lbm1".format(ll=ll, ll1=ll1)
#         coords1 = ll.split(',')
#         coords2 = ll1.split(',')
#         ll2 = f'{(float(coords1[0]) + float(coords2[0])) / 2},{(float(coords1[1]) + float(coords2[1])) / 2}'
#         static_api_request = "http://static-maps.yandex.ru/1.x/?ll={ll2}&spn=0.01,0.01&l=map&pt={point}".format(**locals())
#         print(static_api_request)
