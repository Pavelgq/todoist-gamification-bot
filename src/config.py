from dotenv import load_dotenv
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TODOIST_CLIENT_ID = os.getenv('TODOIST_CLIENT_ID')
    TODOIST_CLIENT_SECRET = os.getenv('TODOIST_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('TODOIST_REDIRECT_URI')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./todoist_bot.db')  # Значение по умолчанию
    
    @classmethod
    def validate(cls):
        """Проверяет наличие всех необходимых переменных окружения."""
        missing_vars = []
        
        if not cls.TELEGRAM_TOKEN:
            missing_vars.append('TELEGRAM_BOT_TOKEN')
        if not cls.TODOIST_CLIENT_ID:
            missing_vars.append('TODOIST_CLIENT_ID')
        if not cls.TODOIST_CLIENT_SECRET:
            missing_vars.append('TODOIST_CLIENT_SECRET')
        if not cls.REDIRECT_URI:
            missing_vars.append('TODOIST_REDIRECT_URI')
            
        if missing_vars:
            error_msg = f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Все переменные окружения настроены корректно")
        return True