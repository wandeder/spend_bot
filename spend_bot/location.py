import requests
import os
from dadata import Dadata

def get_location_reply(location):
    url_geo_yandex = "https://geocode-maps.yandex.ru/1.x/"
    lat = location.latitude
    lon = location.longitude
    currency = {"data": {}}
    yandex_query = {
        "results": "1",
        "geocode": f"{lon},{lat}",
        "apikey": os.getenv("YANDEX_GEO_KEY"),
        "format": "json",
    }
    result = {
        "Страна": "",
        "Валюта": "",
        "Код валюты": "",
        "10 USD = ": 0,
        "1000 RUB = ": 0,
    }

    response = requests.get(url_geo_yandex, params=yandex_query)

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
        currency = dadata.suggest("currency", result["Страна"])[0]

        if currency.get("data").get("name"):
            result["Валюта"] = currency.get("data").get("name")
            result["Код валюты"] = currency.get("data").get("strcode")

    fixer_url = "https://openexchangerates.org/api/latest.json"
    fixer_query = {
        "app_id": os.getenv("FIXER_KEY"),
        "base": "USD",
    }
    usd_convert_list = requests.get(fixer_url, params=fixer_query).json()
    usd_rates = usd_convert_list.get("rates").get(result["Код валюты"])
    result["10 USD = "] = round(10 * usd_rates, 2)
    result["1000 RUB = "] = round((1000 / usd_convert_list.get("rates").get("RUB")) * usd_rates, 2)

    return result
