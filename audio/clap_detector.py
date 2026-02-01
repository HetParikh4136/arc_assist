import time
import numpy as np
from collections import deque

class ClapDetector:
    def __init__(self, threshold, interval, debug=False):
        self.threshold = threshold
        self.interval = interval
        self.debug = debug

        self.clap_times = []
        self.last_clap_time = 0
        self.previous_amplitude = 0
        self.amplitude_history = deque(maxlen=10)

    def detect(self, pcm):
        audio = np.array(pcm, dtype=np.int16)
        amplitude = np.abs(audio).max()
        now = time.time()

        self.amplitude_history.append(amplitude)

        amplitude_jump = amplitude - self.previous_amplitude
        sharp = amplitude_jump > self.threshold * 0.4
        loud = amplitude > self.threshold

        sustained = (
            sum(self.amplitude_history) / len(self.amplitude_history)
            < self.threshold * 0.5
            if len(self.amplitude_history) >= 3 else True
        )

        is_clap = loud and (sharp or sustained)

        if is_clap and now - self.last_clap_time > 0.1:
            self.clap_times.append(now)
            self.last_clap_time = now

            self.clap_times = [t for t in self.clap_times if now - t < self.interval * 2.5]

            if len(self.clap_times) >= 3 and self.clap_times[-1] - self.clap_times[-3] < self.interval * 2.5:
                self.clap_times.clear()
                return 3

            if len(self.clap_times) >= 2 and self.clap_times[-1] - self.clap_times[-2] < self.interval:
                self.clap_times.clear()
                return 2

        self.previous_amplitude = amplitude
        return 0
