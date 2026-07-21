from kivy.config import Config
from math import hypot
import re

# Configure the native window before Kivy creates it. This prevents the OS from
# reopening the app with an oversized or inconsistent geometry.
Config.set("graphics", "width", "1024")
Config.set("graphics", "height", "640")
Config.set("graphics", "minimum_width", "900")
Config.set("graphics", "minimum_height", "600")
Config.set("graphics", "resizable", "1")
Config.set("graphics", "fullscreen", "0")

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from kivy.properties import StringProperty
from kivy.animation import Animation
from kivy.clock import Clock
from threading import Thread
import requests

from app.api_router import fetch_feature

Window.fullscreen = False
Window.size = (1024, 640)
Window.minimum_width = 900
Window.minimum_height = 600


class ChatScreen(BoxLayout):
    dark_mode = BooleanProperty(True)
    theme_ripple_center = ListProperty([0, 0])
    theme_ripple_radius = NumericProperty(0)
    theme_ripple_opacity = NumericProperty(0)
    theme_ripple_color = ListProperty([0.075, 0.10, 0.16, 1])
    _theme_event = None
    page_title = StringProperty("Welcome to\nAPI Assistant")
    page_subtitle = StringProperty("Your friendly workspace for exploring useful public APIs.")
    response_text = StringProperty("Choose a tool from the sidebar, or ask a question to get started.")
    is_loading = BooleanProperty(False)
    typing_dots = NumericProperty(1)
    chat_session = NumericProperty(0)
    _typing_event = None

    def on_kv_post(self, _base_widget):
        for button in self.walk():
            if isinstance(button, ThemedNavButton) and "Main Chat" in button.text:
                button.bind(on_release=lambda _button: self.open_main_chat())
                continue
            if isinstance(button, ThemedNavButton) and "Weather" in button.text:
                button.bind(on_release=lambda _button: self.load_feature("weather"))
                break

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode

    def start_theme_transition(self, center):
        if self._theme_event:
            self._theme_event.cancel()
        Animation.cancel_all(self, "theme_ripple_radius", "theme_ripple_opacity")

        next_is_dark = not self.dark_mode
        self.theme_ripple_center = list(center)
        self.theme_ripple_radius = 0
        self.theme_ripple_opacity = 1
        self.theme_ripple_color = (
            [0.075, 0.10, 0.16, 1]
            if next_is_dark
            else [0.975, 0.985, 1, 1]
        )
        max_radius = max(
            hypot(center[0] - x, center[1] - y)
            for x, y in ((self.x, self.y), (self.right, self.y),
                         (self.x, self.top), (self.right, self.top))
        )
        Animation(theme_ripple_radius=max_radius * 1.10, duration=0.56, t="out_quad").start(self)
        self._theme_event = Clock.schedule_once(self._apply_theme_transition, 0.50)

    def _apply_theme_transition(self, _dt):
        self.toggle_theme()
        Animation(theme_ripple_opacity=0, duration=0.20, t="out_quad").start(self)
        self._theme_event = None

    def load_feature(self, feature, query=""):
        self.page_title = feature.title()
        self.page_subtitle = "Fetching live information..."
        self.response_text = "Please wait a moment."
        self._start_typing_indicator()
        Thread(target=self._fetch_feature, args=(feature, query, self.chat_session), daemon=True).start()

    def _fetch_feature(self, feature, query, session):
        try:
            title, response = fetch_feature(feature, query)
            Clock.schedule_once(lambda _dt: self._show_result(title, response, session))
        except (requests.RequestException, ValueError, KeyError, IndexError) as error:
            Clock.schedule_once(lambda _dt: self._show_result("Unable to load data", str(error), session))

    def _show_result(self, title, response, session):
        if session != self.chat_session:
            return
        self._stop_typing_indicator()
        self.page_title = title
        self.page_subtitle = "Live data from a public API"
        self.response_text = response

    def new_chat(self):
        """Clear the current session and keep focus in the message composer."""
        self.chat_session += 1
        self._stop_typing_indicator()
        self.page_title = "Welcome to\nAPI Assistant"
        self.page_subtitle = "Your friendly workspace for exploring useful public APIs."
        self.response_text = "Choose a tool from the sidebar, or ask a question to get started."
        self.ids.query_input.text = ""
        Clock.schedule_once(lambda _dt: setattr(self.ids.query_input, "focus", True))

    def open_main_chat(self):
        self.chat_session += 1
        self._stop_typing_indicator()
        self.page_title = "Main Chat"
        self.page_subtitle = "General conversation"
        self.response_text = (
            "Hi! I can currently check live weather using Open-Meteo. "
            "Try: What is the weather in Tokyo?"
        )
        self.ids.query_input.text = ""
        Clock.schedule_once(lambda _dt: setattr(self.ids.query_input, "focus", True))

    def _start_typing_indicator(self):
        self.is_loading = True
        self.typing_dots = 1
        if not self._typing_event:
            self._typing_event = Clock.schedule_interval(self._advance_typing_indicator, 0.35)

    def _advance_typing_indicator(self, _dt):
        self.typing_dots = 1 if self.typing_dots >= 3 else self.typing_dots + 1

    def _stop_typing_indicator(self):
        self.is_loading = False
        if self._typing_event:
            self._typing_event.cancel()
            self._typing_event = None

    def send_query(self):
        query = self.ids.query_input.text.strip()
        if not query:
            return
        self.ids.query_input.text = ""
        place = self._weather_location(query)
        if place is not None:
            self.load_feature("weather", place)
            return

        self.page_title = "Main Chat"
        self.page_subtitle = "General conversation"
        if query.lower().strip("!?.") in {"hi", "hello", "hey"}:
            self.response_text = "Hello! Ask me about the weather in any city."
        else:
            self.response_text = (
                "I do not have a general AI model connected yet, but I can check live weather. "
                'Try: "What is the weather in Tokyo?"'
            )

    @staticmethod
    def _weather_location(query):
        """Return a place from a natural-language weather question, if present."""
        normalized = query.strip().rstrip("?!.")
        if "weather" not in normalized.lower():
            return None

        place_match = re.search(r"\b(?:in|at|for)\s+(.+)$", normalized, flags=re.IGNORECASE)
        if place_match:
            return place_match.group(1).strip()

        weather_match = re.search(r"\bweather\s+(.+)$", normalized, flags=re.IGNORECASE)
        if weather_match:
            candidate = weather_match.group(1).strip()
            if candidate.lower() not in {"today", "now", "like"}:
                return candidate
        return "Manila"


class ThemedNavButton(Button):
    dark_mode = BooleanProperty(True)


class ChatInput(TextInput):
    """Text input with a reliable custom blinking caret for the chat composer."""

    caret_visible = BooleanProperty(True)
    _caret_event = None

    def on_focus(self, _instance, focused):
        if focused:
            self.caret_visible = True
            if not self._caret_event:
                self._caret_event = Clock.schedule_interval(self._blink_caret, 0.5)
        elif self._caret_event:
            self._caret_event.cancel()
            self._caret_event = None
            self.caret_visible = False

    def on_text(self, _instance, _value):
        self.caret_visible = True

    def _blink_caret(self, _dt):
        self.caret_visible = not self.caret_visible

class APIAssistant(App):

    def build(self):
        self.title = "API Assistant"

        # Load the KV rules
        Builder.load_file("app/ui/chatbot.kv")

        # Return the root widget
        return ChatScreen()


if __name__ == "__main__":
    APIAssistant().run()
