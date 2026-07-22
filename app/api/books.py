"""Open Library book-search client."""

import requests


TIMEOUT = 12


def search_books(query="The Hobbit"):
    response = requests.get(
        "https://openlibrary.org/search.json",
        params={"q": query, "limit": 5, "fields": "title,author_name,first_publish_year,edition_count"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    books = response.json().get("docs", [])
    if not books:
        raise ValueError(f"I could not find books matching '{query}'.")
    lines = []
    for index, book in enumerate(books, 1):
        author = ", ".join(book.get("author_name", ["Unknown author"])[:2])
        year = book.get("first_publish_year", "Unknown year")
        editions = book.get("edition_count", 0)
        lines.append(f"{index}. {book.get('title', 'Untitled')}\n   {author} · {year} · {editions} editions")
    return f"Books: {query}", "\n\n".join(lines)
