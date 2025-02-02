import os
from dotenv import load_dotenv
import logging
import sys

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
    # Telegram Configuration
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    EMBEDDING_MODEL = "text-embedding-ada-002"
    GPT_MODEL = "gpt-4o-mini"
    
    # Vector Store Configuration
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    # File Storage
    UPLOAD_DIR = "uploads"
    
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_DIR, exist_ok=True) 