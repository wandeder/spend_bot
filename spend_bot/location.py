import requests
import os

def get_location_reply(location):
    url_geo_yandex = "https://geocode-maps.yandex.ru/1.x/"
    lat = location.latitude
    lon = location.longitude
    query = {
        "results": "1",
        "geocode": f"{lat},{lon}",
        "apikey": os.getenv("YANDEX_GEO_KEY"),
        "format": "json",
        "kind": "country",
    }
    result = {
        "Страна": None,
        "Код": None,
        "Валюта": None,
        "Код валюты": None,
    }

    response = requests.get(url_geo_yandex, params=query)

    data = response.json()

    return data
