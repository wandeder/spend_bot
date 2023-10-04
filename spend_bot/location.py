import requests
import os
from dadata import Dadata

def get_location_reply(location):
    url_geo_yandex = "https://geocode-maps.yandex.ru/1.x/"
    lat = location.latitude
    lon = location.longitude
    query = {
        "results": "1",
        "geocode": f"{lon},{lat}",
        "apikey": os.getenv("YANDEX_GEO_KEY"),
        "format": "json",
    }
    result = {
        "Страна": "",
        "Валюта": "",
        "Код валюты": "",
    }

    response = requests.get(url_geo_yandex, params=query)

    data = response.json().get("response")
    country = (
        data.get("GeoObjectCollection")
        .get("featureMember")[0]
        .get("GeoObject")
        .get("metaDataProperty")
        .get("GeocoderMetaData")
        .get("Address")

    )
    if country.get("Components")[0].get("kind") == "country":
        result["Страна"] = country.get("Components")[0].get("name")

        dadata = Dadata(os.getenv("DADATA_KEY"))
        currency = dadata.suggest("country", result["Страна"])[0]

        if currency.get("data").get("name"):
            result["Валюта"] = currency.get("data").get("name")
            result["Код валюты"] = currency.get("data").get("strcode")
            result["test"] = dadata.suggest("country", result["Страна"])

    return result
