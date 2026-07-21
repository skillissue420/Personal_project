"""Route Explore features to their dedicated API clients."""

from app.api.countries import get_country
from app.api.currency import get_exchange_rate
from app.api.dictionary import define_word
from app.api.jokes import get_random_joke
from app.api.nasa import get_astronomy_picture
from app.api.news import get_top_news
from app.api.weather import get_weather


FEATURES = {
    "weather": get_weather,
    "news": lambda _="": get_top_news(),
    "currency": get_exchange_rate,
    "dictionary": define_word,
    "nasa": lambda _="": get_astronomy_picture(),
    "countries": get_country,
    "jokes": lambda _="": get_random_joke(),
}


def fetch_feature(feature, query=""):
    if feature not in FEATURES:
        raise ValueError("Choose an item from Explore to get started.")
    return FEATURES[feature](query) if query else FEATURES[feature]()
