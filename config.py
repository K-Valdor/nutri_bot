import os
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    telegram_token: str = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_user_id: int = int(os.getenv("ADMIN_USER_ID", "0"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/nutrition.db")
    
    @classmethod
    def validate(cls):
        if not cls.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
        if not cls.admin_user_id:
            raise ValueError("ADMIN_USER_ID not set")

config = Config()
