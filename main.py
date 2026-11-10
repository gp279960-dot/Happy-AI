import os
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from assistant import initialize, set_api_key, ask_jarvis
from android_voice import AndroidVoice
from android_tts import AndroidTTS

try:
    from android.permissions import request_permissions, Permission
    ANDROID = True
except ImportError:
    ANDROID = False


class HappyAI(App):

    def build(self):
        self.title = "Happy AI"
        self.listening_enabled = False
        self.voice = None
        self.tts = None

        font_path = os.path.join(
            os.path.dirname(__file__),
            "assets",
            "NotoSansDevanagari-Regular.ttf"
        )

        if os.path.exists(font_path):
            LabelBase.register(
                name="Marathi",
                fn_regular=font_path
            )
            self.font = "Marathi"
        else:
            self.font = "Roboto"

        initialize(self.user_data_dir)

        root = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        self.status = Label(
            text="हॅप्पी तयार आहे",
            font_name=self.font,
            font_size=dp(22),
            size_hint_y=None,
            height=dp(55)
        )
        root.add_widget(self.status)

        self.question = Label(
            text="तुम्ही काय बोललात ते येथे दिसेल",
            font_name=self.font,
            font_size=dp(18)
        )
        root.add_widget(self.question)

        self.answer = Label(
            text="हॅप्पीचे उत्तर येथे दिसेल",
            font_name=self.font,
            font_size=dp(18)
        )
        root.add_widget(self.answer)

        self.api_input = TextInput(
            hint_text="Gemini API Key",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(self.api_input)

        save_button = Button(
            text="API KEY SAVE",
            size_hint_y=None,
            height=dp(48)
        )
        save_button.bind(on_press=self.save_key)
        root.add_widget(save_button)

        self.mic_button = Button(
            text="🎤 START HAPPY",
            font_size=dp(22),
            size_hint_y=None,
            height=dp(75)
        )
        self.mic_button.bind(on_press=self.toggle_voice)
        root.add_widget(self.mic_button)

        self.voice = AndroidVoice(
            on_result=self.on_voice_result,
            on_status=self.update_status
        )

        self.tts = AndroidTTS(
            on_complete=self.on_speech_complete
        )

        if ANDROID:
            request_permissions(
                [Permission.RECORD_AUDIO],
                self.permission_callback
            )

        return root

    def permission_callback(self, permissions, grants):
        if grants and all(grants):
            self.update_status("माइक परवानगी मिळाली.")
        else:
            self.update_status("माइक परवानगी आवश्यक आहे.")

    def save_key(self, instance):
        key = self.api_input.text.strip()

        if key:
            set_api_key(key)
            self.api_input.text = ""
            self.update_status("API Key सुरक्षित केली!")
        else:
            self.update_status("आधी API Key टाका.")

    def toggle_voice(self, instance):
        if self.listening_enabled:
            self.listening_enabled = False
            self.voice.stop()
            self.tts.stop()
            self.mic_button.text = "🎤 START HAPPY"
            self.update_status("माइक बंद आहे.")
        else:
            self.listening_enabled = True
            self.mic_button.text = "⏹ STOP HAPPY"
            self.start_listening()

    def start_listening(self):
        if self.listening_enabled:
            self.voice.start()

    def on_voice_result(self, words):
        if not self.listening_enabled:
            return

        words = str(words).strip()
        if not words:
            Clock.schedule_once(
                lambda dt: self.start_listening(), 0.5
            )
            return

        self.question.text = "तुम्ही: " + words
        self.update_status("हॅप्पी विचार करत आहे...")

        threading.Thread(
            target=self.get_answer,
            args=(words,),
            daemon=True
        ).start()

    def get_answer(self, words):
        answer = ask_jarvis(words)
        Clock.schedule_once(
            lambda dt: self.show_answer(answer), 0
        )

    def show_answer(self, answer):
        self.answer.text = "हॅप्पी: " + str(answer)
        self.update_status("हॅप्पी बोलत आहे...")
        if self.listening_enabled:
            self.tts.speak(answer)

    def on_speech_complete(self):
        if self.listening_enabled:
            self.update_status("हॅप्पी पुन्हा ऐकत आहे...")
            self.start_listening()

    def update_status(self, message):
        Clock.schedule_once(
            lambda dt: setattr(self.status, "text", str(message)),
            0
        )

    def on_stop(self):
        self.listening_enabled = False

        if self.voice:
            self.voice.stop()

        if self.tts:
            self.tts.shutdown()


if __name__ == "__main__":
    HappyAI().run()
