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

def get_telegram_token():
    """Get Telegram token with detailed logging."""
    # Try different methods to get the token
    token_from_environ = dict(os.environ).get('TELEGRAM_BOT_TOKEN')
    token_from_getenv = os.getenv('TELEGRAM_BOT_TOKEN')
    
    logger.info("=== Telegram Token Debug ===")
    logger.info(f"Token exists in os.environ: {'TELEGRAM_BOT_TOKEN' in os.environ}")
    logger.info(f"Token exists in os.environ.get(): {token_from_environ is not None}")
    logger.info(f"Token exists in os.getenv(): {token_from_getenv is not None}")
    logger.info("===========================")
    
    return token_from_environ or token_from_getenv

class Config:
    # Get Railway service variables
    RAILWAY_ENVIRONMENT_NAME = os.getenv('RAILWAY_ENVIRONMENT_NAME', 'development')
    RAILWAY_SERVICE_NAME = os.getenv('RAILWAY_SERVICE_NAME', 'local')
    
    # Debug: Print all environment variables at class level
    logger.info("=== Environment Variables ===")
    for env_key in sorted(os.environ.keys()):
        value = os.environ[env_key]
        if any(s in env_key.lower() for s in ['token', 'key', 'secret', 'password']):
            logger.info(f"{env_key}=<hidden>")
        else:
            logger.info(f"{env_key}={value}")
    logger.info("===========================")
    
    # Bot Configuration
    TELEGRAM_TOKEN = get_telegram_token()
    if not TELEGRAM_TOKEN:
        logger.error("Failed to get TELEGRAM_BOT_TOKEN")
        logger.error(f"Current environment: {RAILWAY_ENVIRONMENT_NAME}")
        logger.error(f"Current service: {RAILWAY_SERVICE_NAME}")
        raise ValueError(
            "TELEGRAM_BOT_TOKEN not found in environment variables. "
            "Please set it in Railway's environment variables."
        )
    else:
        logger.info("Successfully loaded TELEGRAM_BOT_TOKEN")

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