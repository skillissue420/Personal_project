"""Open-Meteo weather and location lookup client."""

import requests

TIMEOUT = 12


def get_weather(place="Manila"):
    locations = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": place, "count": 1}, timeout=TIMEOUT,
    )
    locations.raise_for_status()
    results = locations.json().get("results", [])
    if not results:
        raise ValueError(f"I could not find a location named '{place}'.")

    location = results[0]
    forecast = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": location["latitude"], "longitude": location["longitude"],
            "current": "temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
        }, timeout=TIMEOUT,
    )
    forecast.raise_for_status()
    current = forecast.json()["current"]
    return (
        f"Weather in {location['name']}, {location.get('country', '')}",
        f"Temperature: {current['temperature_2m']} C\n"
        f"Feels like: {current['apparent_temperature']} C\n"
        f"Wind: {current['wind_speed_10m']} km/h\n"
        f"Weather code: {current['weather_code']}",
    )
