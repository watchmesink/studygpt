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

# Load environment variables
load_dotenv()

# Get tokens directly
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("No Telegram token found in environment variables")
    logger.error("Available environment variables: " + ", ".join(os.environ.keys()))
    raise ValueError("TELEGRAM_BOT_TOKEN not found in environment")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("No OpenAI API key found in environment variables")
    raise ValueError("OPENAI_API_KEY not found in environment")

class Config:
    # Tokens
    TELEGRAM_TOKEN = TELEGRAM_TOKEN
    OPENAI_API_KEY = OPENAI_API_KEY
    
    # Model configurations
    EMBEDDING_MODEL = "text-embedding-ada-002"
    GPT_MODEL = "gpt-4"
    
    # Chunking configurations
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    # File storage
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    
    # Create upload directory
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate all required configurations are present."""
        logger.info("Validating configuration...")
        logger.info(f"Using Telegram token: {cls.TELEGRAM_TOKEN[:10]}...")
        logger.info(f"Using OpenAI key: {cls.OPENAI_API_KEY[:10]}...")
        logger.info(f"Upload directory: {cls.UPLOAD_DIR}") 