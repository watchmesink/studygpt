import os
import sys
from dotenv import load_dotenv
import logging

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log')
    ]
)

logger = logging.getLogger(__name__)

# Debug: Print current working directory
logger.info(f"Current working directory: {os.getcwd()}")

# Load .env file
env_path = os.path.join(os.getcwd(), '.env')
logger.info(f"Looking for .env file at: {env_path}")
if os.path.exists(env_path):
    logger.info(".env file found")
    load_dotenv(env_path)
else:
    logger.warning(".env file not found")

# Debug: Print all environment variables (excluding sensitive values)
logger.info("Environment variables:")
for key in sorted(os.environ.keys()):
    if 'TOKEN' in key or 'KEY' in key:
        logger.info(f"{key}=<hidden>")
    else:
        logger.info(f"{key}={os.environ.get(key)}")

class Config:
    # Try to get token with fallback
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found")
        # Try fallback
        TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
        if TELEGRAM_TOKEN:
            logger.info("Using fallback TELEGRAM_TOKEN")
        else:
            logger.error("No telegram token found in any variable")
            raise ValueError("No telegram token found. Set TELEGRAM_BOT_TOKEN in environment")

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        logger.error("OPENAI_API_KEY not found")
        raise ValueError("No OpenAI API key found. Set OPENAI_API_KEY in environment")
    
    # Model configurations
    EMBEDDING_MODEL = "text-embedding-ada-002"
    GPT_MODEL = "gpt-4"
    
    # Chunking configurations
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    # File storage
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    @classmethod
    def validate(cls):
        """Print current configuration values (safely)"""
        logger.info("=== Current Configuration ===")
        logger.info(f"TELEGRAM_TOKEN: {'<set>' if cls.TELEGRAM_TOKEN else '<missing>'}")
        logger.info(f"OPENAI_API_KEY: {'<set>' if cls.OPENAI_API_KEY else '<missing>'}")
        logger.info(f"UPLOAD_DIR: {cls.UPLOAD_DIR}")
        logger.info(f"EMBEDDING_MODEL: {cls.EMBEDDING_MODEL}")
        logger.info(f"GPT_MODEL: {cls.GPT_MODEL}")
        logger.info("=========================") 