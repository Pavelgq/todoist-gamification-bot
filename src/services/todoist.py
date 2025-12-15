from typing import Optional

from ..database import SessionLocal
from ..models import User

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

    @staticmethod
    def user_has_token(telegram_id: int) -> bool:
        """Проверить, авторизован ли пользователь в Todoist (есть ли токен)."""
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            return bool(user and getattr(user, "todoist_token", None))

    @staticmethod
    def upsert_user_token(telegram_id: int, access_token: str) -> None:
        """Создать пользователя (если нет) и сохранить todoist_token."""
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == telegram_id).first()
            if not user:
                user = User(telegram_id=telegram_id)
                db.add(user)
            user.todoist_token = access_token
            db.commit()
