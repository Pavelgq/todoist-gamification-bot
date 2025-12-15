from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from ..api.todoist_client import TodoistAuthHelper
from ..services.todoist import TodoistService
from ..utils.logger import get_logger
from ..utils.texts import Messages

logger = get_logger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        logger.info("Пользователь запустил бота", user_id=user.id, username=user.username)

        if TodoistService.user_has_token(user.id):
            await update.message.reply_text(Messages.START_ALREADY_AUTHORIZED)
        else:
            state = str(user.id)
            auth_url = TodoistAuthHelper.get_auth_url(state)

            await update.message.reply_text(
                Messages.START_AUTH_REQUEST,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                Messages.START_AUTH_BUTTON,
                                url=auth_url,
                            )
                        ]
                    ]
                ),
            )

            await update.message.reply_text(Messages.START_AFTER_AUTH)

    except Exception as e:
        logger.exception("Ошибка в команде start", error=str(e), user_id=update.effective_user.id)
        await update.message.reply_text(Messages.START_ERROR)
