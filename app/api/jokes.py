"""Official Joke API client."""

import requests


def get_random_joke():
    response = requests.get("https://official-joke-api.appspot.com/random_joke", timeout=12)
    response.raise_for_status()
    data = response.json()
    return "Random joke", f"{data['setup']}\n\n{data['punchline']}"
