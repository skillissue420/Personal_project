"""Lightweight intent detection for routing Main Chat messages to public APIs."""

import re


def detect_intent(message):
    text = message.lower()
    rules = (
        ("weather", ("weather", "forecast", "temperature", "rain")),
        ("news", ("news", "headline", "headlines")),
        ("currency", ("currency", "exchange rate", "convert", "conversion")),
        ("dictionary", ("define", "definition", "meaning", "dictionary")),
        ("nasa", ("nasa", "space", "astronomy", "apod")),
        ("countries", ("country", "capital", "population", "languages")),
        ("jokes", ("joke", "funny", "make me laugh")),
    )
    for intent, keywords in rules:
        if any(keyword in text for keyword in keywords):
            return intent
    return None


def intent_query(intent, message):
    """Extract the portion of a natural-language message useful to each API."""
    text = message.strip().rstrip("?!.")
    if intent == "currency":
        codes = re.findall(r"\b[A-Za-z]{3}\b", text.upper())
        return " ".join(codes[:2])
    if intent == "dictionary":
        match = re.search(r"(?:define|definition of|meaning of)\s+(.+)$", text, re.IGNORECASE)
        return match.group(1).strip() if match else "assistant"
    if intent == "countries":
        match = re.search(r"(?:country|capital|population|languages?)\s+(?:of|in)\s+(.+)$", text, re.IGNORECASE)
        return match.group(1).strip() if match else "Philippines"
    return ""
