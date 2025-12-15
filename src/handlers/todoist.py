from telegram import Update
from telegram.ext import ContextTypes

from ..api.todoist_client import TodoistClient
from ..services.todoist import TodoistService
from ..utils.auth import check_auth
from ..utils.logger import get_logger
from ..utils.texts import Messages

logger = get_logger(__name__)

async def show_tags(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_user.id
        logger.info("Запрос списка тегов", user_id=user_id)
        user = TodoistService.get_user_by_telegram_id(user_id) 
        if not await check_auth(update, user):
            return

        client = TodoistClient(user.todoist_token)
        tags = client.get_labels()
        if not tags:
            logger.info("У пользователя нет тегов", user_id=user_id)
            await update.message.reply_text(Messages.TAGS_NONE)
            return

        label_names = [tag.name.strip() for tag in tags if getattr(tag, "name", None)]
        if label_names:
            message = Messages.TAGS_LIST_HEADER + "\n".join(label_names)
            await update.message.reply_text(message)
            logger.info("Список тегов отправлен", user_id=user_id, tags_count=len(label_names))
        else:
            logger.info("У пользователя нет тегов (пустой список после фильтрации)", user_id=user_id)
            await update.message.reply_text(Messages.TAGS_NONE)
    except Exception as e:
        logger.exception("Ошибка при получении тегов", error=str(e), user_id=update.effective_user.id)
        await update.message.reply_text(Messages.TAGS_ERROR)

