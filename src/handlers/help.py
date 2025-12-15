from telegram import Update
from telegram.ext import ContextTypes

from ..utils.logger import get_logger
from ..utils.texts import Messages

logger = get_logger(__name__)


async def show_help(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user_id = update.effective_user.id if update.effective_user else None
        logger.info("Запрос справки", user_id=user_id)
        if update.message:
            await update.message.reply_text(Messages.HELP_TEXT)
        elif update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.edit_message_text(Messages.HELP_TEXT)
        else:
            logger.warning("show_help вызван без message или callback_query", user_id=user_id)
        logger.info("Справка отправлена", user_id=user_id)
    except Exception as e:
        logger.exception("Ошибка в show_help", error=str(e), user_id=update.effective_user.id if update.effective_user else None)
        if update.effective_message:
            await update.effective_message.reply_text(Messages.HELP_ERROR)
