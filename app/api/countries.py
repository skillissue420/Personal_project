"""REST Countries client."""

import requests


def get_country(country="Philippines"):
    response = requests.get(f"https://restcountries.com/v3.1/name/{country}", params={"fullText": "false"}, timeout=12)
    response.raise_for_status()
    data = response.json()[0]
    capital = ", ".join(data.get("capital", ["Not listed"]))
    languages = ", ".join(data.get("languages", {}).values()) or "Not listed"
    currencies = ", ".join(data.get("currencies", {}).keys()) or "Not listed"
    return data.get("name", {}).get("common", country), (
        f"Capital: {capital}\nRegion: {data.get('region', 'Not listed')}\n"
        f"Population: {data.get('population', 0):,}\nLanguages: {languages}\nCurrencies: {currencies}"
    )
