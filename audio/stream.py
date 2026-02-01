import sounddevice as sd

class AudioStream:
    def __init__(self, sample_rate, frame_length):
        self.sample_rate = sample_rate
        self.frame_length = frame_length
        self.stream = None

    def start(self):
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=self.frame_length
        )
        self.stream.start()

    def read(self):
        audio_data, _ = self.stream.read(self.frame_length)
        return audio_data.flatten().tolist()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
