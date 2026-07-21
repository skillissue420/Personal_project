"""Free Dictionary API client."""

import requests

TIMEOUT = 12


def define_word(word="assistant"):
    response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=TIMEOUT)
    response.raise_for_status()
    entry = response.json()[0]
    definitions = []
    for meaning in entry.get("meanings", [])[:2]:
        definition = meaning.get("definitions", [{}])[0].get("definition", "")
        definitions.append(f"{meaning.get('partOfSpeech', '').title()}: {definition}")
    return f"Definition: {entry.get('word', word)}", "\n\n".join(definitions)
