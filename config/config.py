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
    # Try to get token from Railway environment first, then fall back to .env
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("No Telegram token found in environment variables")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("No OpenAI API key found in environment variables")
    
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
            raise ValueError(f"Missing required configuration variables: {', '.join(missing)}")
        
        logger.info("Configuration validation successful")

    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True) 