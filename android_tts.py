from jnius import autoclass, PythonJavaClass, java_method
from plyer.platforms.android import activity
from kivy.clock import Clock

TextToSpeech = autoclass("android.speech.tts.TextToSpeech")
Locale = autoclass("java.util.Locale")


class TTSListener(PythonJavaClass):
    __javainterfaces__ = [
        "android/speech/tts/TextToSpeech$OnInitListener"
    ]
    __javacontext__ = "app"

    def __init__(self, owner):
        super().__init__()
        self.owner = owner

    @java_method("(I)V")
    def onInit(self, status):
        self.owner.ready = status == TextToSpeech.SUCCESS
        if self.owner.ready:
            result = self.owner.tts.setLanguage(Locale("mr", "IN"))
            if result < TextToSpeech.LANG_AVAILABLE:
                self.owner.tts.setLanguage(Locale("hi", "IN"))


class TTSProgressListener(PythonJavaClass):
    __javainterfaces__ = [
        "android/speech/tts/UtteranceProgressListener"
    ]
    __javacontext__ = "app"

    def __init__(self, owner):
        super().__init__()
        self.owner = owner

    @java_method("(Ljava/lang/String;)V")
    def onStart(self, utteranceId):
        pass

    @java_method("(Ljava/lang/String;)V")
    def onDone(self, utteranceId):
        if self.owner.on_complete:
            Clock.schedule_once(
                lambda dt: self.owner.on_complete(), 0
            )

    @java_method("(Ljava/lang/String;)V")
    def onError(self, utteranceId):
        pass


class AndroidTTS:
    def __init__(self, on_complete=None):
        self.ready = False
        self.tts = None
        self.on_complete = on_complete

        self.listener = TTSListener(self)
        self.progress_listener = TTSProgressListener(self)

        self.tts = TextToSpeech(activity, self.listener)
        self.tts.setOnUtteranceProgressListener(
            self.progress_listener
        )

    def speak(self, message):
        if not message or not self.ready:
            return

        self.tts.speak(
            str(message),
            TextToSpeech.QUEUE_FLUSH,
            None,
            "happy_reply"
        )

    def stop(self):
        if self.tts:
            self.tts.stop()

    def shutdown(self):
        if self.tts:
            self.tts.stop()
            self.tts.shutdown()
            self.tts = None
