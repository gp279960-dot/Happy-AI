import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from assistant import initialize, set_api_key, ask_jarvis


class HappyAI(App):

    def build(self):
        self.title = "Happy AI"
        initialize(self.user_data_dir)

        layout = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        layout.add_widget(Label(
            text="😊 HAPPY AI",
            font_size=30,
            size_hint_y=0.12
        ))

        self.api_input = TextInput(
            hint_text="Gemini API Key",
            password=True,
            multiline=False,
            size_hint_y=0.10
        )

        api_button = Button(
            text="API Key सेट करा",
            size_hint_y=0.10
        )
        api_button.bind(on_press=self.set_key)

        self.output = Label(
            text="नमस्कार बॉस! मी हॅप्पी आहे.",
            halign="left",
            valign="top"
        )
        self.output.bind(size=self.output.setter("text_size"))

        self.message = TextInput(
            hint_text="बॉस, येथे प्रश्न लिहा...",
            multiline=False,
            size_hint_y=0.12
        )

        send = Button(
            text="पाठवा",
            size_hint_y=0.12
        )
        send.bind(on_press=self.send_message)

        layout.add_widget(self.api_input)
        layout.add_widget(api_button)
        layout.add_widget(self.output)
        layout.add_widget(self.message)
        layout.add_widget(send)

        return layout

    def set_key(self, instance):
        key = self.api_input.text.strip()
        if key:
            set_api_key(key)
            self.output.text = "बॉस, API Key सेट झाली!"

    def send_message(self, instance):
        question = self.message.text.strip()
        if not question:
            return

        self.message.text = ""
        self.output.text = "हॅप्पी विचार करत आहे..."

        threading.Thread(
            target=self.get_answer,
            args=(question,),
            daemon=True
        ).start()

    def get_answer(self, question):
        answer = ask_jarvis(question)
        Clock.schedule_once(
            lambda dt: self.show_answer(question, answer)
        )

    def show_answer(self, question, answer):
        self.output.text = (
            "बॉस: " + question +
            "\n\nहॅप्पी: " + answer
        )


if __name__ == "__main__":
    HappyAI().run()
