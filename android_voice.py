
from plyer import stt
from kivy.clock import Clock


class AndroidVoice:

    def __init__(self, on_result, on_status):
        self.on_result = on_result
        self.on_status = on_status
        self.active = False
        self.poll_event = None

        stt.language = "mr-IN"
        stt.prefer_offline = False

    def start(self):
        if self.active:
            return

        try:
            if not stt.exist():
                self.on_status("Speech Recognition उपलब्ध नाही.")
                return

            stt.results.clear()
            stt.errors.clear()
            stt.partial_results.clear()

            self.active = True
            stt.start()

            self.on_status("🎤 हॅप्पी ऐकत आहे...")

            self.poll_event = Clock.schedule_interval(
                self.check_result, 0.3
            )

        except Exception as error:
            self.active = False
            self.on_status("माइक Error: " + str(error))

    def check_result(self, dt):
        if not self.active:
            return False

        if stt.results:
            words = list(stt.results)
            stt.results.clear()

            self.stop()
            if words:
                self.on_result(words[0])

        elif stt.errors:
            errors = list(stt.errors)
            stt.errors.clear()

            self.stop()
            self.on_status("ऐकण्यात अडचण: " + str(errors[-1]))

    def stop(self):
        self.active = False

        if self.poll_event:
            self.poll_event.cancel()
            self.poll_event = None

        try:
            stt.stop()
        except Exception:
            pass

        self.on_status("माइक बंद आहे.")
