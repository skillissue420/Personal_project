"""Art Institute of Chicago collection-search client."""

import requests


TIMEOUT = 12


def search_art(query="impressionism"):
    response = requests.get(
        "https://api.artic.edu/api/v1/artworks/search",
        params={"q": query, "limit": 5, "fields": "id,title,artist_title,date_display"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    artworks = response.json().get("data", [])
    if not artworks:
        raise ValueError(f"I could not find artwork matching '{query}'.")
    return f"Art: {query}", "\n\n".join(
        f"{index}. {artwork.get('title', 'Untitled')}\n"
        f"   {artwork.get('artist_title') or 'Unknown artist'} · {artwork.get('date_display') or 'Date unknown'}"
        for index, artwork in enumerate(artworks, 1)
    )
