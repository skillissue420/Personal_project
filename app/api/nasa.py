"""NASA Astronomy Picture of the Day client."""

import requests


def get_astronomy_picture():
    response = requests.get("https://api.nasa.gov/planetary/apod", params={"api_key": "DEMO_KEY"}, timeout=12)
    response.raise_for_status()
    data = response.json()
    return f"NASA: {data.get('title', 'Astronomy Picture of the Day')}", data.get("explanation", "")[:900]
