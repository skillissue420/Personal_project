"""Hacker News client for the News view."""

import requests

TIMEOUT = 12


def get_top_news():
    response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=TIMEOUT)
    response.raise_for_status()
    story_ids = response.json()[:5]
    stories = []
    for story_id in story_ids:
        story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=TIMEOUT)
        story.raise_for_status()
        stories.append(story.json())
    return "Top Hacker News", "\n\n".join(
        f"{index}. {story.get('title', 'Untitled')}" for index, story in enumerate(stories, 1)
    )
