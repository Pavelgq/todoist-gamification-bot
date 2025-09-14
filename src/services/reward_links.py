from ..models import RewardLink, SessionLocal
from typing import List, Optional
import logging
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

class RewardLinkService:

    @staticmethod
    def create_link(user_id: int, reward_id: int, tag_id: int, value: float) -> RewardLink:
        """Создает новую связь награды с тегом."""
        with SessionLocal() as db:
            try:
                link = RewardLink(
                    user_id=user_id,
                    reward_id=reward_id,
                    tag_id=tag_id,
                    value=value
                )
                db.add(link)
                db.commit()
                db.refresh(link)
                return link
            except Exception as e:
                db.rollback()
                logger.error("Error creating link", exc_info=True)
                raise

    @staticmethod
    def get_user_links(user_id: int) -> List[RewardLink]:
        """Возвращает все связи пользователя."""
        with SessionLocal() as db:
            return db.query(RewardLink).options(joinedload(RewardLink.reward)).filter(RewardLink.user_id == user_id).all()

    @staticmethod
    def get_link_by_id(link_id: int) -> Optional[RewardLink]:
        """Находит связь по ID."""
        with SessionLocal() as db:
            return db.query(RewardLink).options(joinedload(RewardLink.reward)).filter(RewardLink.id == link_id).first()

    @staticmethod
    def get_links_by_reward(user_id: int, reward_id: int) -> List[RewardLink]:
        """Возвращает все связи по награде."""
        with SessionLocal() as db:
            return db.query(RewardLink).options(joinedload(RewardLink.reward)).filter((RewardLink.user_id == user_id) & (RewardLink.id == reward_id)).all()


    @staticmethod
    def update_link_value(link_id: int, new_value: float) -> Optional[RewardLink]:
        """Обновляет значение связи."""
        with SessionLocal() as db:
            try:
                link = db.query(RewardLink).filter(RewardLink.id == link_id).first()
                if link:
                    link.value = new_value
                    db.commit()
                    db.refresh(link)
                return link
            except Exception as e:
                db.rollback()
                logger.error("Error updating link", exc_info=True)
                raise

    @staticmethod
    def delete_link(link_id: int) -> bool:
        """Удаляет связь."""
        with SessionLocal() as db:
            try:
                link = db.query(RewardLink).filter(RewardLink.id == link_id).first()
                if link:
                    db.delete(link)
                    db.commit()
                    return True
                return False
            except Exception as e:
                db.rollback()
                logger.error("Error deleting link", exc_info=True)
                raise

    @staticmethod
    def find_existing_link(user_id: int, reward_id: int, tag_id: int) -> Optional[RewardLink]:
        """Проверяет существование связи по user, reward, tag."""
        with SessionLocal() as db:
            return db.query(RewardLink).filter(
                RewardLink.user_id == user_id,
                RewardLink.reward_id == reward_id,
                RewardLink.tag_id == tag_id
            ).first()
