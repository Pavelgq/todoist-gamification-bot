from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.orm import joinedload

from ..database import SessionLocal
from ..models import Reward
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RewardDTO:
    id: int
    name: str
    unit: str


class RewardService:
    @staticmethod
    def _to_dto(reward: Reward) -> RewardDTO:
        return RewardDTO(
            id=reward.id,
            name=reward.name,
            unit=reward.unit,
        )

    @staticmethod
    def get_user_rewards(user_id: int) -> List[RewardDTO]:
        """Получить все награды пользователя как простые DTO."""
        with SessionLocal() as db:
            rewards = (
                db.query(Reward)
                .options(joinedload(Reward.reward_links))
                .filter(Reward.user_id == user_id)
                .all()
            )
            return [RewardService._to_dto(r) for r in rewards]

    @staticmethod
    def create_reward(user_id: int, name: str, unit: str) -> RewardDTO:
        """Создать награду пользователю и вернуть DTO, а не ORM-модель."""
        with SessionLocal() as db:
            try:
                reward = Reward(user_id=user_id, name=name, unit=unit)
                db.add(reward)
                db.commit()
                db.refresh(reward)
                return RewardService._to_dto(reward)
            except Exception:
                db.rollback()
                logger.error("Ошибка создания награды", exc_info=True)
                raise

    @staticmethod
    def get_reward_by_id(reward_id: int) -> Optional[RewardDTO]:
        """Получить награду по id как DTO."""
        with SessionLocal() as db:
            reward = db.query(Reward).filter(Reward.id == reward_id).first()
            return RewardService._to_dto(reward) if reward else None
