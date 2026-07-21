"""Small, dependency-free clients for the APIs exposed in the desktop UI."""

from __future__ import annotations

import requests

TIMEOUT = 12


def _get(url, **params):
    response = requests.get(url, params=params, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def weather(place="Manila"):
    places = _get("https://geocoding-api.open-meteo.com/v1/search", name=place, count=1)
    if not places.get("results"):
        raise ValueError(f"I could not find a location named '{place}'.")
    location = places["results"][0]
    forecast = _get(
        "https://api.open-meteo.com/v1/forecast",
        latitude=location["latitude"], longitude=location["longitude"],
        current="temperature_2m,apparent_temperature,weather_code,wind_speed_10m",
    )["current"]
    return (
        f"Weather in {location['name']}, {location.get('country', '')}",
        f"Temperature: {forecast['temperature_2m']} C\n"
        f"Feels like: {forecast['apparent_temperature']} C\n"
        f"Wind: {forecast['wind_speed_10m']} km/h\n"
        f"Weather code: {forecast['weather_code']}",
    )


def news():
    story_ids = _get("https://hacker-news.firebaseio.com/v0/topstories.json")[:5]
    stories = [_get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json") for story_id in story_ids]
    lines = [f"{index}. {story.get('title', 'Untitled')}" for index, story in enumerate(stories, 1)]
    return "Top Hacker News", "\n\n".join(lines)


def currency(query="USD PHP"):
    parts = query.upper().split()
    base, target = (parts + ["USD", "PHP"])[:2] if len(parts) >= 2 else ("USD", "PHP")
    data = _get("https://api.frankfurter.dev/v1/latest", base=base, symbols=target)
    rate = data["rates"].get(target)
    if rate is None:
        raise ValueError("Use ISO currency codes, for example: USD PHP")
    return f"{base} to {target}", f"1 {base} = {rate:,.4f} {target}\nUpdated: {data['date']}"


def dictionary(word="assistant"):
    entry = _get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")[0]
    meanings = entry.get("meanings", [])
    definitions = []
    for meaning in meanings[:2]:
        definition = meaning.get("definitions", [{}])[0].get("definition", "")
        definitions.append(f"{meaning.get('partOfSpeech', '').title()}: {definition}")
    return f"Definition: {entry.get('word', word)}", "\n\n".join(definitions)


def nasa():
    data = _get("https://api.nasa.gov/planetary/apod", api_key="DEMO_KEY")
    explanation = data.get("explanation", "No explanation provided.")
    return f"NASA: {data.get('title', 'Astronomy Picture of the Day')}", explanation[:900]


def countries(country="Philippines"):
    data = _get(f"https://restcountries.com/v3.1/name/{country}", fullText="false")[0]
    capital = ", ".join(data.get("capital", ["Not listed"]))
    languages = ", ".join(data.get("languages", {}).values()) or "Not listed"
    currencies = ", ".join(data.get("currencies", {}).keys()) or "Not listed"
    return data.get("name", {}).get("common", country), (
        f"Capital: {capital}\nRegion: {data.get('region', 'Not listed')}\n"
        f"Population: {data.get('population', 0):,}\nLanguages: {languages}\nCurrencies: {currencies}"
    )


def jokes():
    data = _get("https://official-joke-api.appspot.com/random_joke")
    return "Random joke", f"{data['setup']}\n\n{data['punchline']}"


FEATURES = {
    "weather": weather, "news": lambda _="": news(), "currency": currency,
    "dictionary": dictionary, "nasa": lambda _="": nasa(), "countries": countries,
    "jokes": lambda _="": jokes(),
}


def fetch_feature(feature, query=""):
    if feature not in FEATURES:
        raise ValueError("Choose an item from Explore to get started.")
    return FEATURES[feature](query) if query else FEATURES[feature]()
