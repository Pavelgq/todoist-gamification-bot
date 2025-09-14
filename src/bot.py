import threading
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from .handlers.start import start
from .handlers.statistic import show_stats
from .handlers.todoist import show_tags
from .handlers.rewards import get_rewards_handlers
from .models import init_db
from .server import run_server
from .config import Config

import logging


# Включим логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

async def handle_auth_callback(update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="Авторизация прошла успешно!")


def main():
    try:
        # Проверяем конфигурацию
        Config.validate()
        
        # Инициализация БД
        init_db()

        # Запускаем сервер
        threading.Thread(target=run_server, daemon=True).start()
        
        # Создаем Application
        application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        return
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}", exc_info=True)
        return

    rewards_handlers = get_rewards_handlers()
    for handler in rewards_handlers:
        application.add_handler(handler)
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("tags", show_tags))
    application.add_handler(CommandHandler("statistic", show_stats))
    application.add_handler(CallbackQueryHandler(handle_auth_callback))
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()