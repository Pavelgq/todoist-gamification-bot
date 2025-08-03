from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TODOIST_CLIENT_ID = os.getenv('TODOIST_CLIENT_ID')
    TODOIST_CLIENT_SECRET = os.getenv('TODOIST_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('TODOIST_REDIRECT_URI')
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Добавьте проверку
    @classmethod
    def validate(cls):
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set in .env file")