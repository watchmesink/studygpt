import os
import sys
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

# Debug: Print all environment variables
logger.info("Available environment variables:")
for key in sorted(os.environ.keys()):
    if 'TOKEN' in key or 'KEY' in key or 'SECRET' in key:
        logger.info(f"{key}=<hidden>")
    else:
        logger.info(f"{key}={os.environ.get(key)}")

class Config:
    # Get Railway service variables
    RAILWAY_ENVIRONMENT_NAME = os.getenv('RAILWAY_ENVIRONMENT_NAME', 'development')
    RAILWAY_SERVICE_NAME = os.getenv('RAILWAY_SERVICE_NAME', 'local')
    
    # Bot Configuration
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')  # Using get directly from environ
    if not TELEGRAM_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN not found in environment variables. "
            "Please set it in Railway's environment variables."
        )

    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')  # Using get directly from environ
    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in Railway's environment variables."
        )
    
    # Model configurations
    EMBEDDING_MODEL = "text-embedding-ada-002"
    GPT_MODEL = "gpt-4o-mini"
    
    # Chunking configurations
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    # File storage - use Railway's persistent storage path if available
    UPLOAD_DIR = os.getenv('RAILWAY_VOLUME_MOUNT_PATH', 'uploads')
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    @classmethod
    def validate(cls):
        """Print current configuration values (safely)"""
        logger.info("=== Current Configuration ===")
        logger.info(f"Environment: {cls.RAILWAY_ENVIRONMENT_NAME}")
        logger.info(f"Service: {cls.RAILWAY_SERVICE_NAME}")
        logger.info(f"TELEGRAM_TOKEN: {'<set>' if cls.TELEGRAM_TOKEN else '<missing>'}")
        logger.info(f"OPENAI_API_KEY: {'<set>' if cls.OPENAI_API_KEY else '<missing>'}")
        logger.info(f"UPLOAD_DIR: {cls.UPLOAD_DIR}")
        logger.info("=========================") 