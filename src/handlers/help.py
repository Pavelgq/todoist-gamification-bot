import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


HELP_TEXT = (
    "📋 Список доступных команд:\n\n"
    "• /start — начать работу с ботом и авторизовать Todoist.\n"
    "• /help — показать это сообщение со списком команд.\n"
    "• /tags — показать список ваших тегов в Todoist.\n"
    "• /statistic [период] — показать статистику по наградам за период (доступно: неделя, месяц, '3 месяца').\n"
    "• /newreward — создать новую награду.\n"
    "• /setreward — привязать награду к тегу Todoist.\n"
    "• /rewards — показать ваши добавленные награды.\n"
)


async def show_help(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.message:
            await update.message.reply_text(HELP_TEXT)
        elif update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(HELP_TEXT)
        else:
            logger.warning("show_help called without message or callback_query")
    except Exception as e:
        logger.error("Error in show_help: %s", e, exc_info=True)
        if update.effective_message:
            await update.effective_message.reply_text("❌ Ошибка при выводе списка команд.")
