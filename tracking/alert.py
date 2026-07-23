import threading
import pyttsx3


class VoiceAlert:

    def __init__(self):
        self.speaking = False

    def speak(self, message):

        if self.speaking:
            return

        self.speaking = True

        threading.Thread(
            target=self._run,
            args=(message,),
            daemon=True
        ).start()

    def _run(self, message):

        try:
            # Create a NEW engine every time
            engine = pyttsx3.init()

            engine.setProperty("rate", 160)
            engine.setProperty("volume", 1.0)

            engine.say(message)
            engine.runAndWait()
            engine.stop()

        finally:
            self.speaking = False


voice_alert = VoiceAlert()