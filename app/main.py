from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

Window.size = (1400, 850)
Window.minimum_width = 1100
Window.minimum_height = 700


class ChatScreen(BoxLayout):
    pass


class APIAssistant(App):

    def build(self):
        self.title = "API Assistant"

        Builder.load_file("app/ui/chatbot.kv")
        Builder.load_file("app/ui/sidebar.kv")

        return ChatScreen()


if __name__ == "__main__":
    APIAssistant().run()