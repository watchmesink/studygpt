import os
import sys
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load .env file if it exists (local development)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)

class Config:
    @classmethod
    def get_telegram_token(cls):
        """Get Telegram token with fallback logic."""
        token = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
        logger.info(f"Using {'Railway' if os.getenv('TELEGRAM_BOT_TOKEN') else 'local'} Telegram token")
        return token

    @classmethod
    def get_openai_key(cls):
        """Get OpenAI API key."""
        key = os.getenv("OPENAI_API_KEY")
        logger.info("OpenAI API key is" + (" not" if not key else "") + " configured")
        return key

    # Telegram Configuration
    TELEGRAM_TOKEN = get_telegram_token()
    if not TELEGRAM_TOKEN:
        logger.error("No Telegram token found in environment variables")
        logger.error("Available environment variables: " + ", ".join(os.environ.keys()))
        raise ValueError("No Telegram token found. Set TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN")
    
    # OpenAI Configuration
    OPENAI_API_KEY = get_openai_key()
    if not OPENAI_API_KEY:
        logger.error("No OpenAI API key found in environment variables")
        raise ValueError("No OpenAI API key found. Set OPENAI_API_KEY")
    
    # Model configurations
    EMBEDDING_MODEL = "text-embedding-ada-002"
    GPT_MODEL = "gpt-4"
    
    # Chunking configurations
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    # File storage
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    
    @classmethod
    def validate(cls):
        """Validate all required configurations are present."""
        logger.info("Validating configuration...")
        required_vars = {
            "TELEGRAM_TOKEN": cls.TELEGRAM_TOKEN,
            "OPENAI_API_KEY": cls.OPENAI_API_KEY,
            "UPLOAD_DIR": cls.UPLOAD_DIR
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            logger.error(f"Missing required configuration: {', '.join(missing)}")
            raise ValueError(f"Missing required configuration variables: {', '.join(missing)}")
        
        logger.info("Configuration validation successful")
        logger.info(f"Upload directory: {cls.UPLOAD_DIR}")

    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True) 