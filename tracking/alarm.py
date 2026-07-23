import threading
import winsound


class Alarm:

    def __init__(self):
        self.alarm_running = False

    def play_alarm(self):

        if self.alarm_running:
            return

        self.alarm_running = True

        thread = threading.Thread(
            target=self._beep,
            daemon=True
        )

        thread.start()

    def _beep(self):

        try:

            # Three warning beeps

            for _ in range(3):
                winsound.Beep(1800, 300)
                winsound.Beep(1200, 200)

        finally:
            self.alarm_running = False


alarm = Alarm()