from ..models import Reward, SessionLocal
from typing import List, Optional
import logging
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

class RewardService:
    @staticmethod
    def get_user_rewards(user_id: int) -> List[Reward]:
        """Получить все награды пользователя."""
        with SessionLocal() as db:
            return db.query(Reward).options(joinedload(Reward.reward_links)).filter(Reward.user_id == user_id).all()

    @staticmethod
    def create_reward(user_id: int, name: str, unit: str) -> Reward:
        """Создать награду пользователю."""
        with SessionLocal() as db:
            try:
                reward = Reward(user_id=user_id, name=name, unit=unit)
                db.add(reward)
                db.commit()
                db.refresh(reward)
                return reward
            except Exception as e:
                db.rollback()
                logger.error("Ошибка создания награды", exc_info=True)
                raise

    @staticmethod
    def get_reward_by_id(reward_id: int) -> Optional[Reward]:
        """Получить награду по id."""
        with SessionLocal() as db:
            return db.query(Reward).filter(Reward.id == reward_id).first()
