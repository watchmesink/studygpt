import os
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SecretManager:
    """Manages application secrets from multiple sources."""
    
    @staticmethod
    def _read_json_file(file_path):
        """Read secrets from a JSON file."""
        try:
            with open(file_path) as f:
                return json.load(f)
        except Exception as e:
            logger.debug(f"Could not read JSON file {file_path}: {e}")
            return {}

    @staticmethod
    def _read_env_file(file_path):
        """Read secrets from .env file."""
        secrets = {}
        try:
            with open(file_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        secrets[key.strip()] = value.strip()
        except Exception as e:
            logger.debug(f"Could not read env file {file_path}: {e}")
        return secrets

    @classmethod
    def get_secrets(cls):
        """Get secrets from all possible sources."""
        secrets = {}
        
        # 1. Check environment variables first (Railway)
        secrets.update({
            'TELEGRAM_TOKEN': os.environ.get('TELEGRAM_TOKEN'),
            'TELEGRAM_BOT_TOKEN': os.environ.get('TELEGRAM_BOT_TOKEN'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY')
        })
        
        # 2. Check for secrets.json in various locations
        paths_to_check = [
            Path(__file__).parent / 'secrets.json',
            Path(__file__).parent.parent / 'secrets.json',
            Path.home() / '.config' / 'studygpt' / 'secrets.json'
        ]
        
        for path in paths_to_check:
            if path.exists():
                secrets.update(cls._read_json_file(path))
        
        # 3. Check for .env file
        env_path = Path(__file__).parent.parent / '.env'
        if env_path.exists():
            secrets.update(cls._read_env_file(env_path))
        
        # Log found secrets (without values)
        logger.info("=== Available Secrets ===")
        for key in secrets:
            if secrets[key] is not None:
                logger.info(f"Found: {key}")
        logger.info("=======================")
        
        return secrets

# Global secrets instance
_secrets = None

def get_secret(key, default=None):
    """Get a secret by key."""
    global _secrets
    if _secrets is None:
        _secrets = SecretManager.get_secrets()
    return _secrets.get(key, default) 