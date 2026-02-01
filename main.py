import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / 'arc_assist.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from audio.wake_word import WakeWordDetector
    from audio.clap_detector import ClapDetector
    from launcher.controller import UnifiedController
    from config import DEFAULT_WAKE_WORD, CLAP_THRESHOLD, CLAP_INTERVAL
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    print(f"❌ Import Error: {e}")
    sys.exit(1)
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    print(f"❌ Configuration Error: {e}")
    print("Please check your .env file and ensure all required variables are set.")
    sys.exit(1)

def main():
    """Main entry point for Arc Assist."""
    try:
        debug = "--debug" in sys.argv
        
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("Debug mode enabled")
        
        # Validate configuration
        if not DEFAULT_WAKE_WORD:
            raise ValueError("DEFAULT_WAKE_WORD is not configured")
        
        if CLAP_THRESHOLD <= 0:
            raise ValueError(f"CLAP_THRESHOLD must be positive, got {CLAP_THRESHOLD}")
        
        if CLAP_INTERVAL <= 0:
            raise ValueError(f"CLAP_INTERVAL must be positive, got {CLAP_INTERVAL}")
        
        logger.info("Initializing Arc Assist...")
        
        # Initialize detectors
        logger.info(f"Loading wake word from: {DEFAULT_WAKE_WORD}")
        detector = WakeWordDetector(DEFAULT_WAKE_WORD)
        
        logger.info("Initializing clap detector...")
        clap = ClapDetector(CLAP_THRESHOLD, CLAP_INTERVAL, debug)

        # Initialize and run controller
        logger.info("Starting unified controller...")
        controller = UnifiedController(detector, clap)
        controller.run()
        
    except ValueError as e:
        logger.error(f"Configuration validation error: {e}")
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"Required file not found: {e}")
        print(f"❌ File Not Found: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()
