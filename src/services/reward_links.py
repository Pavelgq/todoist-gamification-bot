from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.orm import joinedload

from ..database import SessionLocal
from ..models import RewardLink
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RewardLinkDTO:
    """DTO для связи награды с тегом."""
    id: int
    user_id: int
    reward_id: int
    tag_id: int
    value: float


@dataclass
class UserTokenDTO:
    """DTO для токена пользователя Todoist."""
    telegram_id: int
    todoist_token: str


class RewardLinkService:

    @staticmethod
    def _to_dto(link: RewardLink) -> RewardLinkDTO:
        """Преобразует ORM-модель в DTO."""
        return RewardLinkDTO(
            id=link.id,
            user_id=link.user_id,
            reward_id=link.reward_id,
            tag_id=link.tag_id,
            value=link.value,
        )

    @staticmethod
    def create_link(user_id: int, reward_id: int, tag_id: int, value: float) -> RewardLinkDTO:
        """Создает новую связь награды с тегом и возвращает DTO."""
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
                logger.info("Связь награды с тегом создана", user_id=user_id, reward_id=reward_id, tag_id=tag_id, value=value)
                return RewardLinkService._to_dto(link)
            except Exception as e:
                db.rollback()
                logger.exception("Ошибка при создании связи награды с тегом", error=str(e), user_id=user_id, reward_id=reward_id, tag_id=tag_id)
                raise

    @staticmethod
    def get_user_links(user_id: int) -> List[RewardLinkDTO]:
        """Возвращает все связи пользователя как DTO."""
        with SessionLocal() as db:
            links = db.query(RewardLink).options(joinedload(RewardLink.reward)).filter(RewardLink.user_id == user_id).all()
            return [RewardLinkService._to_dto(link) for link in links]

    @staticmethod
    def get_link_by_id(link_id: int) -> Optional[RewardLinkDTO]:
        """Находит связь по ID и возвращает DTO."""
        with SessionLocal() as db:
            link = db.query(RewardLink).options(joinedload(RewardLink.reward)).filter(RewardLink.id == link_id).first()
            return RewardLinkService._to_dto(link) if link else None

    @staticmethod
    def get_links_by_reward(user_id: int, reward_id: int) -> List[RewardLinkDTO]:
        """Возвращает все связи по награде как DTO."""
        with SessionLocal() as db:
            links = db.query(RewardLink).options(joinedload(RewardLink.reward)).filter((RewardLink.user_id == user_id) & (RewardLink.reward_id == reward_id)).all()
            return [RewardLinkService._to_dto(link) for link in links]

    @staticmethod
    def update_link_value(link_id: int, new_value: float) -> Optional[RewardLinkDTO]:
        """Обновляет значение связи и возвращает DTO."""
        with SessionLocal() as db:
            try:
                link = db.query(RewardLink).filter(RewardLink.id == link_id).first()
                if link:
                    link.value = new_value
                    db.commit()
                    db.refresh(link)
                    logger.info("Значение связи обновлено", link_id=link_id, new_value=new_value)
                    return RewardLinkService._to_dto(link)
                return None
            except Exception as e:
                db.rollback()
                logger.exception("Ошибка при обновлении связи награды с тегом", error=str(e), link_id=link_id, new_value=new_value)
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
                    logger.info("Связь удалена", link_id=link_id)
                    return True
                return False
            except Exception as e:
                db.rollback()
                logger.exception("Ошибка при удалении связи награды с тегом", error=str(e), link_id=link_id)
                raise

    @staticmethod
    def find_existing_link(user_id: int, reward_id: int, tag_id: int) -> Optional[RewardLinkDTO]:
        """Проверяет существование связи по user, reward, tag и возвращает DTO или None."""
        with SessionLocal() as db:
            link = db.query(RewardLink).filter(
                RewardLink.user_id == user_id,
                RewardLink.reward_id == reward_id,
                RewardLink.tag_id == tag_id
            ).first()
            return RewardLinkService._to_dto(link) if link else None
