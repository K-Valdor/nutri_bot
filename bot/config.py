import os

class Config:
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    DB_PATH = '/opt/nutrition-bot/data/nutrition.db'
    
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")
