"""Nager.Date public-holidays client."""

import datetime as dt

import requests


TIMEOUT = 12
COUNTRY_CODES = {
    "philippines": "PH", "philippine": "PH", "usa": "US", "united states": "US",
    "uk": "GB", "united kingdom": "GB", "england": "GB", "japan": "JP",
    "australia": "AU", "canada": "CA", "india": "IN", "singapore": "SG",
}


def get_holidays(country="PH"):
    normalized = country.strip().lower()
    country_code = COUNTRY_CODES.get(normalized, country.strip().upper())
    if len(country_code) != 2 or not country_code.isalpha():
        raise ValueError("Use a country name or two-letter country code, for example: Philippines or PH")
    year = dt.date.today().year
    response = requests.get(f"https://date.nager.at/api/v4/Holidays/{country_code}/{year}", timeout=TIMEOUT)
    response.raise_for_status()
    holidays = response.json()
    upcoming = [holiday for holiday in holidays if holiday["date"] >= dt.date.today().isoformat()][:5]
    shown = upcoming or holidays[:5]
    if not shown:
        raise ValueError(f"No public holidays were returned for {country_code}.")
    return f"Public holidays: {country_code}", "\n".join(
        f"{holiday['date']} — {holiday['name']}" for holiday in shown
    )
