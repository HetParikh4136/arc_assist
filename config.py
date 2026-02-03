
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Validate required environment variables
def _get_required_env(var_name: str, description: str) -> str:
    """Get required environment variable with validation."""
    value = os.getenv(var_name)
    if not value:
        raise ValueError(
            f"Missing required environment variable: {var_name}\n"
            f"Description: {description}\n"
            f"Please set it in your .env file"
        )
    return value

def _get_optional_env(var_name: str, default: str) -> str:
    """Get optional environment variable with default fallback."""
    return os.getenv(var_name, default)

def _get_int_env(var_name: str, default: int) -> int:
    """Get integer environment variable with validation."""
    try:
        return int(os.getenv(var_name, str(default)))
    except ValueError:
        raise ValueError(f"Invalid integer value for {var_name}")

# API Keys (Required)
PORCUPINE_ACCESS_KEY = _get_required_env(
    "PORCUPINE_ACCESS_KEY",
    "Porcupine API access key from https://console.picovoice.ai"
)

# Wake Word Configuration
DEFAULT_WAKE_WORD = _get_optional_env(
    "WAKE_WORD_PATH",
    str(Path(__file__).parent / "Hey arc.ppn")
)

# Validate wake word file exists
if not Path(DEFAULT_WAKE_WORD).exists():
    raise FileNotFoundError(
        f"Wake word file not found: {DEFAULT_WAKE_WORD}\n"
        f"Please check WAKE_WORD_PATH in your .env file"
    )

# Audio Configuration
CLAP_THRESHOLD = _get_int_env("CLAP_THRESHOLD", 1800)
ACTIVE_DURATION = _get_int_env("ACTIVE_DURATION", 5)
TRIPLE_WAIT_DURATION = _get_int_env("TRIPLE_WAIT_DURATION", 30)
CLAP_INTERVAL = float(os.getenv("CLAP_INTERVAL", "0.7"))

# Debug mode
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# LLM Configuration for Q&A (Optional)
# Default: OpenRouter with free Llama 3.1 8B model
# To enable: Set LLM_API_KEY in your .env file
# Get your key from: https://openrouter.ai/keys
#
# Example .env configuration:
# LLM_API_KEY=your_openrouter_api_key
# (API_BASE and MODEL default to OpenRouter's Llama 3.1 8B)
#
# To use a different provider/model:
# LLM_API_BASE=https://api.openai.com/v1  (for OpenAI)
# LLM_MODEL=gpt-4o-mini  (for OpenAI)
# Or any OpenAI-compatible API endpoint
