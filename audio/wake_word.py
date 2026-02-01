import pvporcupine
from config import PORCUPINE_ACCESS_KEY
import os

class WakeWordDetector:
    def __init__(self, wake_word):
        # Check if wake_word is a path to a custom .ppn file
        if wake_word.endswith('.ppn') and os.path.isfile(wake_word):
            self.porcupine = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY,
                keyword_paths=[wake_word]
            )
        else:
            # Use built-in keyword
            self.porcupine = pvporcupine.create(
                access_key=PORCUPINE_ACCESS_KEY,
                keywords=[wake_word]
            )

    @property
    def sample_rate(self):
        return self.porcupine.sample_rate

    @property
    def frame_length(self):
        return self.porcupine.frame_length

    def detect(self, pcm):
        return self.porcupine.process(pcm) >= 0

    def cleanup(self):
        self.porcupine.delete()
