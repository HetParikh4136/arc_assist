import time
import logging
from audio.stream import AudioStream
from audio.clap_detector import ClapDetector
from launcher.app_launcher import AppLauncher
from config import ACTIVE_DURATION, TRIPLE_WAIT_DURATION

logger = logging.getLogger(__name__)

class UnifiedController:
    def __init__(self, wake_detector, clap_detector):
        if not wake_detector or not clap_detector:
            raise ValueError("Wake detector and clap detector cannot be None")
        
        self.wake_detector = wake_detector
        self.clap_detector = clap_detector
        self.launcher = AppLauncher()

        self.active = False
        self.active_time = 0
        self.waiting_triple = False
        self.triple_time = 0

        try:
            self.audio = AudioStream(
                wake_detector.sample_rate,
                wake_detector.frame_length
            )
        except Exception as e:
            logger.error(f"Failed to initialize audio stream: {e}")
            raise

    def run(self):
        """Main control loop for wake word and clap detection."""
        try:
            self.audio.start()
            print("🎧 Listening...\n")

            while True:
                try:
                    pcm = self.audio.read()
                    
                    if pcm is None or len(pcm) == 0:
                        continue

                    if not self.active and not self.waiting_triple:
                        if self.wake_detector.detect(pcm):
                            self.active = True
                            self.active_time = time.time()
                            print("✨ Wake word detected!")

                    elif self.active:
                        # Check if active duration has expired
                        if time.time() - self.active_time > ACTIVE_DURATION:
                            self.active = False
                            continue

                        clap = self.clap_detector.detect(pcm)
                        if clap == 2:
                            try:
                                self.launcher.launch_apps()
                            except Exception as e:
                                logger.error(f"Error launching apps: {e}")
                                print(f"❌ Error launching apps: {e}")
                            
                            self.active = False
                            self.waiting_triple = True
                            self.triple_time = time.time()

                    elif self.waiting_triple:
                        # Check if triple wait duration has expired
                        if time.time() - self.triple_time > TRIPLE_WAIT_DURATION:
                            self.waiting_triple = False
                            continue

                        if self.clap_detector.detect(pcm) == 3:
                            try:
                                self.launcher.open_url()
                            except Exception as e:
                                logger.error(f"Error opening URL: {e}")
                                print(f"❌ Error opening URL: {e}")
                            
                            self.waiting_triple = False

                except KeyboardInterrupt:
                    print("\n👋 Shutting down...")
                    break
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    print(f"❌ Error in main loop: {e}")
                    continue

        except KeyboardInterrupt:
            print("\n👋 Shutting down...")
        except Exception as e:
            logger.error(f"Fatal error in controller: {e}")
            print(f"❌ Fatal error: {e}")
        finally:
            try:
                self.audio.stop()
                print("✅ Audio stream closed")
            except Exception as e:
                logger.error(f"Error closing audio stream: {e}")
