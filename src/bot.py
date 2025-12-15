import os
import threading

from telegram import BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

from .handlers.start import start
from .handlers.statistic import show_stats
from .handlers.todoist import show_tags
from .handlers.rewards import get_rewards_handlers
from .handlers.help import show_help
from .models import init_db
from .server import run_server
from .config import Config
from .utils.logger import setup_logging, get_logger
from .utils.texts import Messages

# Настраиваем структурированное логирование
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(level=log_level)

logger = get_logger(__name__)


async def handle_auth_callback(update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id if update.effective_user else None
    logger.info("Обработка callback авторизации", user_id=user_id)
    await query.answer()
    await query.edit_message_text(text=Messages.AUTH_SUCCESS)


async def post_init(application: Application) -> None:
    """Регистрируем команды бота для контекстного меню Telegram."""
    await application.bot.set_my_commands(
        [
            BotCommand("start", Messages.COMMAND_START_DESC),
            BotCommand("help", Messages.COMMAND_HELP_DESC),
            BotCommand("tags", Messages.COMMAND_TAGS_DESC),
            BotCommand("statistic", Messages.COMMAND_STATISTIC_DESC),
            BotCommand("newreward", Messages.COMMAND_NEWREWARD_DESC),
            BotCommand("setreward", Messages.COMMAND_SETREWARD_DESC),
            BotCommand("rewards", Messages.COMMAND_REWARDS_DESC),
        ]
    )


def main():
    try:
        # Проверяем конфигурацию
        Config.validate()

        # Инициализация БД
        init_db()

        # Запускаем сервер
        threading.Thread(target=run_server, daemon=True).start()

        # Создаем Application
        application = (
            Application.builder()
            .token(Config.TELEGRAM_TOKEN)
            .post_init(post_init)
            .build()
        )
    except ValueError as e:
        logger.error("Ошибка конфигурации", error=str(e))
        return
    except Exception as e:
        logger.exception("Ошибка запуска", error=str(e))
        return

    rewards_handlers = get_rewards_handlers()
    for handler in rewards_handlers:
        application.add_handler(handler)

    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CommandHandler("tags", show_tags))
    application.add_handler(CommandHandler("statistic", show_stats))

    application.add_handler(CallbackQueryHandler(handle_auth_callback))

    # Запускаем бота
    application.run_polling()


if __name__ == "__main__":
    main()
