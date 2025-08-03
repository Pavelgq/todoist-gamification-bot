from src.models import User

async def check_auth(update, user) -> bool:
    """
    Проверяет, что пользователь авторизован.
    Если не авторизован — пишет сообщение и возвращает False.
    """
    if not user or not getattr(user, "todoist_token", None):
        await update.message.reply_text("Сначала авторизуйтесь через /start")
        return False
    return True
