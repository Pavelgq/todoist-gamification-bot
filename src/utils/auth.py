from ..models import User
from .texts import Messages
from .logger import get_logger

logger = get_logger(__name__)

async def check_auth(update, user) -> bool:
    """
    Проверяет, что пользователь авторизован.
    Если не авторизован — пишет сообщение и возвращает False.
    Поддерживает как message, так и callback_query.
    """
    user_id = update.effective_user.id if update.effective_user else None
    if not user or not getattr(user, "todoist_token", None):
        logger.warning("Попытка доступа без авторизации", user_id=user_id)
        if update.message:
            await update.message.reply_text(Messages.AUTH_REQUIRED)
        elif update.callback_query:
            await update.callback_query.answer(Messages.AUTH_REQUIRED, show_alert=True)
        return False
    return True
