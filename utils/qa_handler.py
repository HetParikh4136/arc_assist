import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class QAHandler:
    """Handles question-answering using LLM APIs."""
    
    def __init__(self):
        self.api_key = os.getenv("LLM_API_KEY")
        self.api_base = os.getenv("LLM_API_BASE", "https://openrouter.ai/api/v1")
        self.model = os.getenv("LLM_MODEL", "mistralai/mistral-7b-instruct:free")
        fallback_env = os.getenv("LLM_FALLBACK_MODELS", "meta-llama/llama-3.1-8b-instruct:free")
        self.fallback_models = [m.strip() for m in fallback_env.split(",") if m.strip()]
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("LLM API key not configured. Q&A functionality disabled.")
            logger.info("To enable Q&A, set LLM_API_KEY in your .env file")
        else:
            logger.info(f"Q&A enabled with model: {self.model}")
    
    def answer_question(self, question: str) -> Optional[str]:
        """
        Send question to LLM and get answer.
        
        Args:
            question: The user's question
            
        Returns:
            The LLM's answer, or None if failed
        """
        if not self.enabled:
            return "Q&A is not configured. Please set LLM_API_KEY in your .env file."
        
        try:
            import requests

            headers = {
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json"
            }

            models_to_try = [self.model] + [m for m in self.fallback_models if m != self.model]
            last_error = None

            for model in models_to_try:
                payload = {
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are Arc, a helpful voice assistant. Provide concise, clear answers (2-3 sentences max). Be friendly and direct."
                        },
                        {
                            "role": "user",
                            "content": question
                        }
                    ],
                    "max_tokens": 150,
                    "temperature": 0.7
                }

                try:
                    response = requests.post(
                        f"{self.api_base}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=10
                    )
                except requests.exceptions.Timeout:
                    last_error = "timeout"
                    logger.warning(f"API request timed out for model {model}. Trying next fallback.")
                    continue

                if response.status_code == 200:
                    if not response.text:
                        last_error = "empty response"
                        logger.warning(f"Empty response for model {model}. Trying next fallback.")
                        continue
                    try:
                        data = response.json()
                        answer = data["choices"][0]["message"]["content"].strip()
                        return answer
                    except Exception as parse_error:
                        last_error = f"invalid JSON ({parse_error})"
                        logger.warning(f"Invalid JSON for model {model}. Trying next fallback.")
                        continue
                else:
                    last_error = f"API error {response.status_code}"
                    logger.warning(f"API error {response.status_code} for model {model}: {response.text}. Trying next fallback.")
                    continue

            logger.error(f"All model attempts failed. Last error: {last_error}")
            return "Sorry, I couldn't get a response from any model."

        except ImportError:
            logger.error("requests library not installed")
            return "Requests library is required for Q&A. Run: pip install requests"
        except Exception as e:
            logger.error(f"Error getting answer: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def text_to_speech(self, text: str):
        """
        Convert text to speech and play it.
        Uses Windows SAPI on Windows, or prints text as fallback.
        
        Args:
            text: The text to speak
        """
        try:
            import platform
            
            if platform.system() == "Windows":
                # Use Windows SAPI
                import pyttsx3
                engine = pyttsx3.init()
                engine.setProperty('rate', 175)  # Speed
                engine.setProperty('volume', 0.9)  # Volume
                engine.say(text)
                engine.runAndWait()
            else:
                # Fallback: just print
                print(f"🗣️ Arc: {text}")
                
        except ImportError:
            # If pyttsx3 not installed, just print
            print(f"🗣️ Arc: {text}")
        except Exception as e:
            logger.error(f"TTS error: {e}")
            print(f"🗣️ Arc: {text}")
