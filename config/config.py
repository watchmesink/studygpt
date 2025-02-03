import os
import sys
from pathlib import Path
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

# Find and load .env file
env_path = Path(__file__).parent.parent / '.env'
logger.info(f"Looking for .env file at: {env_path}")
if env_path.exists():
    logger.info(f"Loading environment variables from {env_path}")
    load_dotenv(env_path)
else:
    logger.warning(f".env file not found at {env_path}")

def get_telegram_token():
    """Get Telegram token with detailed logging."""
    # Try both possible token names
    token = os.getenv('TELEGRAM_BOT_TOKEN') or os.getenv('TELEGRAM_TOKEN')
    
    logger.info("=== Telegram Token Debug ===")
    logger.info(f"TELEGRAM_BOT_TOKEN exists: {'TELEGRAM_BOT_TOKEN' in os.environ}")
    logger.info(f"TELEGRAM_TOKEN exists: {'TELEGRAM_TOKEN' in os.environ}")
    logger.info(f"Final token exists: {token is not None}")
    logger.info(f".env file exists: {env_path.exists()}")
    logger.info("===========================")
    
    return token

def log_environment_variables():
    """Log all environment variables, hiding sensitive ones."""
    logger.info("=== Environment Variables ===")
    for key in sorted(os.environ.keys()):
        value = os.environ[key]
        sensitive_words = ['token', 'key', 'secret', 'password']
        if any(word in key.lower() for word in sensitive_words):
            logger.info(f"{key}=<hidden>")
        else:
            logger.info(f"{key}={value}")
    logger.info("===========================")

class Config:
    # Get Railway service variables
    RAILWAY_ENVIRONMENT_NAME = os.getenv('RAILWAY_ENVIRONMENT_NAME', 'development')
    RAILWAY_SERVICE_NAME = os.getenv('RAILWAY_SERVICE_NAME', 'local')
    
    # Log environment variables
    log_environment_variables()
    
    # Bot Configuration
    TELEGRAM_TOKEN = get_telegram_token()
    if not TELEGRAM_TOKEN:
        logger.error("Failed to get Telegram token")
        logger.error("Tried both TELEGRAM_BOT_TOKEN and TELEGRAM_TOKEN variables")
        logger.error(f"Current environment: {RAILWAY_ENVIRONMENT_NAME}")
        logger.error(f"Current service: {RAILWAY_SERVICE_NAME}")
        raise ValueError(
            "No Telegram token found in environment variables. "
            "Please set either TELEGRAM_BOT_TOKEN or TELEGRAM_TOKEN."
        )
    else:
        logger.info("Successfully loaded Telegram token")

    # OpenAI Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
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
        logger.info(f"TELEGRAM_TOKEN exists: {bool(cls.TELEGRAM_TOKEN)}")
        logger.info(f"OPENAI_API_KEY exists: {bool(cls.OPENAI_API_KEY)}")
        logger.info(f"UPLOAD_DIR: {cls.UPLOAD_DIR}")
        logger.info("=========================")

# Validate configuration on module load
Config.validate() 