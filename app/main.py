from kivy.config import Config
from math import hypot

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
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ListProperty, NumericProperty
from kivy.properties import StringProperty
from kivy.animation import Animation
from kivy.clock import Clock
from threading import Thread

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
        Thread(target=self._fetch_feature, args=(feature, query), daemon=True).start()

    def _fetch_feature(self, feature, query):
        try:
            title, response = fetch_feature(feature, query)
            Clock.schedule_once(lambda _dt: self._show_result(title, response))
        except (requests.RequestException, ValueError, KeyError, IndexError) as error:
            Clock.schedule_once(lambda _dt: self._show_result("Unable to load data", str(error)))

    def _show_result(self, title, response):
        self.page_title = title
        self.page_subtitle = "Live data from a public API"
        self.response_text = response

    def send_query(self):
        query = self.ids.query_input.text.strip()
        if not query:
            return
        self.ids.query_input.text = ""
        parts = query.split(maxsplit=1)
        feature = parts[0].lower()
        aliases = {"country": "countries", "joke": "jokes", "define": "dictionary", "definition": "dictionary"}
        self.load_feature(aliases.get(feature, feature), parts[1] if len(parts) > 1 else "")


class ThemedNavButton(Button):
    dark_mode = BooleanProperty(True)

class APIAssistant(App):

    def build(self):
        self.title = "API Assistant"

        # Load the KV rules
        Builder.load_file("app/ui/chatbot.kv")

        # Return the root widget
        return ChatScreen()


if __name__ == "__main__":
    APIAssistant().run()
