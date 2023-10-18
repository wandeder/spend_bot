import requests
import os
from dadata import Dadata

def get_location_reply(location):
    YANDEX_GEO_URL = os.getenv("YANDEX_GEO_URL", "")
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
        "Страна: ": "",
        "Валюта: ": "",
        "Код валюты: ": "",
        "10 USD = ": 0,
        "1000 RUB = ": 0,
    }

    response = requests.get(YANDEX_GEO_URL, params=yandex_query)

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
        result["Страна: "] = country.get("Components")[0].get("name")

        dadata = Dadata(os.getenv("DADATA_KEY"))
        currency = dadata.suggest("currency", result["Страна: "])[0]

        if currency.get("data").get("name"):
            result["Валюта: "] = currency.get("data").get("name")
            result["Код валюты: "] = currency.get("data").get("strcode")

    FIXER_URL = os.getenv("FIXER_URL", "")
    fixer_query = {
        "app_id": os.getenv("FIXER_KEY"),
        "base": "USD",
    }
    usd_convert_list = requests.get(FIXER_URL, params=fixer_query).json()
    usd_rates = usd_convert_list.get("rates").get(result["Код валюты: "])
    result["10 USD = "] = round(10 * usd_rates, 0)
    result["1000 RUB = "] = round((1000 / usd_convert_list.get("rates").get("RUB")) * usd_rates, 0)

    res_str = [f"{key}{result[key]}\n" for key in result]
    return "".join(res_str)
