from src.models import User, SessionLocal
from typing import Optional

class TodoistService:
    @staticmethod
    def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
        """
        Получить пользователя по telegram_id.

        :param telegram_id: ID пользователя в Telegram.
        :return: User или None, если пользователь не найден.
        """
        with SessionLocal() as db:
            return db.query(User).filter(User.telegram_id == telegram_id).first()
