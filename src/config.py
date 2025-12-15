from dotenv import load_dotenv
import os

from .utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)


class TodoistConfig:
    """Константы и настройки для работы с Todoist API."""
    
    # URLs
    OAUTH_AUTHORIZE_URL = "https://todoist.com/oauth/authorize"
    OAUTH_ACCESS_TOKEN_URL = "https://todoist.com/oauth/access_token"
    
    # OAuth scope
    OAUTH_SCOPE = "data:read_write,data:delete"
    
    # Периоды для статистики (в днях)
    PERIOD_MAP = {
        "неделя": 7,
        "месяц": 30,
        "3 месяца": 90,
    }
    
    # Настройки ретраев для API-вызовов
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1.0


class Config:
    """Основная конфигурация приложения."""
    
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
            logger.error("Отсутствуют обязательные переменные окружения", missing_vars=missing_vars)
            raise ValueError(error_msg)
        
        logger.info("Все переменные окружения настроены корректно")
        return True