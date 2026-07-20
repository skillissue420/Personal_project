from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window

Window.size = (1200, 800)


class ChatScreen(BoxLayout):
    pass


class APIAssistant(App):

    def build(self):
        self.title = "API Assistant"

        Builder.load_file("app/ui/chatbot.kv")

        return ChatScreen()


if __name__ == "__main__":
    APIAssistant().run()