import logging
from src.api.labels import get_labels
from src.services.todoist import TodoistService
from telegram import Update
from telegram.ext import ContextTypes

from src.utils.auth import check_auth

logger = logging.getLogger(__name__)

async def show_tags(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = TodoistService.get_user_by_telegram_id(update.effective_user.id) 
        if not check_auth(update, user):
            return
        if not user or not getattr(user, "todoist_token", None):
            await update.message.reply_text("❌ Не найден пользователь или нет todoist_token.")
            return

        tags = get_labels(user.todoist_token) if callable(getattr(get_labels, "__await__", None)) else get_labels(user.todoist_token)
        if not tags:
            await update.message.reply_text("У вас нет тегов в Todoist")
            return

        label_names = [tag.name.strip() for tag in tags if getattr(tag, "name", None)]
        if label_names:
            message = "Ваши теги:\n" + "\n".join(label_names)
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("У вас нет тегов в Todoist")
    except Exception as e:
        logger.error("Ошибка при получении тегов: %s", e)
        await update.message.reply_text("❌ Ошибка при получении списка тегов.")

