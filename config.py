"""
Central configuration module.
Loads all environment variables from .env file.
"""
import os
from dotenv import load_dotenv

# Load environment variables once at startup
load_dotenv()


class Config:
    """Application configuration from environment variables."""
    
    # Telegram Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'telegram_bot')
    
    # Admin
    ADMIN_IDS = os.getenv('ADMIN_IDS', '1393899188,8504577397')
    
    @classmethod
    def get_admin_ids(cls) -> list:
        """Get list of admin Telegram user IDs."""
        if not cls.ADMIN_IDS:
            return []
        return [int(id.strip()) for id in cls.ADMIN_IDS.split(',') if id.strip().isdigit()]
    
    @classmethod
    def is_admin(cls, telegram_id: int) -> bool:
        """Check if user is admin."""
        return telegram_id in cls.get_admin_ids()
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.BOT_TOKEN:
            return False
        return True
