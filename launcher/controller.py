import time
import logging
import speech_recognition as sr
import sounddevice as sd
import numpy as np
from audio.stream import AudioStream
from audio.clap_detector import ClapDetector
from launcher.app_launcher import AppLauncher
from utils.qa_handler import QAHandler
from config import ACTIVE_DURATION, TRIPLE_WAIT_DURATION

logger = logging.getLogger(__name__)

class UnifiedController:
    def __init__(self, wake_detector, clap_detector):
        if not wake_detector or not clap_detector:
            raise ValueError("Wake detector and clap detector cannot be None")
        
        self.wake_detector = wake_detector
        self.clap_detector = clap_detector
        self.launcher = AppLauncher()
        self.qa_handler = QAHandler()

        self.active = False
        self.active_time = 0
        self.waiting_triple = False
        self.triple_time = 0
        
        # Initialize speech recognizer (no PyAudio needed)
        self.recognizer = sr.Recognizer()

        try:
            self.audio = AudioStream(
                wake_detector.sample_rate,
                wake_detector.frame_length
            )
        except Exception as e:
            logger.error(f"Failed to initialize audio stream: {e}")
            raise

    def listen_for_command(self):
        """Listen for voice command after wake word using sounddevice."""
        try:
            print("🎤 Listening for command...")
            
            # Record audio using sounddevice (16kHz for speech recognition)
            duration = 5  # seconds
            sample_rate = 16000
            audio_data = sd.rec(int(duration * sample_rate), 
                               samplerate=sample_rate, 
                               channels=1, 
                               dtype='int16')
            sd.wait()
            
            # Convert to speech_recognition AudioData format
            audio_data_bytes = audio_data.tobytes()
            audio = sr.AudioData(audio_data_bytes, sample_rate, 2)
                
            try:
                command = self.recognizer.recognize_google(audio).lower()
                print(f"🗣️ You said: {command}")
                return command
            except sr.UnknownValueError:
                print("❓ Could not understand audio")
                return None
            except sr.RequestError as e:
                logger.error(f"Speech recognition service error: {e}")
                print(f"❌ Speech recognition error: {e}")
                return None
        except Exception as e:
            logger.error(f"Error listening for command: {e}")
            print(f"❌ Error capturing audio: {e}")
            return None
    
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
                            
                            # Listen for voice command
                            command = self.listen_for_command()
                            if command:
                                if "the usual" in command:
                                    print("📱 Executing 'the usual' command...")
                                    try:
                                        self.launcher.launch_apps()
                                    except Exception as e:
                                        logger.error(f"Error launching apps: {e}")
                                        print(f"❌ Error launching apps: {e}")
                                else:
                                    # Treat as a question
                                    print("❓ Processing question...")
                                    try:
                                        answer = self.qa_handler.answer_question(command)
                                        if answer:
                                            print(f"💬 Answer: {answer}")
                                            self.qa_handler.text_to_speech(answer)
                                    except Exception as e:
                                        logger.error(f"Error processing question: {e}")
                                        print(f"❌ Error: {e}")
                            self.active = False
                            continue

                    # Keep double clap functionality as backup
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
                            # Commented out triple clap / URL functionality
                            # self.waiting_triple = True
                            # self.triple_time = time.time()

                    # Commented out triple clap / URL functionality
                    # elif self.waiting_triple:
                    #     # Check if triple wait duration has expired
                    #     if time.time() - self.triple_time > TRIPLE_WAIT_DURATION:
                    #         self.waiting_triple = False
                    #         continue
                    #
                    #     if self.clap_detector.detect(pcm) == 3:
                    #         try:
                    #             self.launcher.open_url()
                    #         except Exception as e:
                    #             logger.error(f"Error opening URL: {e}")
                    #             print(f"❌ Error opening URL: {e}")
                    #         
                    #         self.waiting_triple = False

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
