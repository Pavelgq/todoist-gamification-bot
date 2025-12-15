from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Dict

from ..api.todoist_client import TodoistClient
from ..config import TodoistConfig
from ..database import SessionLocal
from ..models import User, RewardLink, Reward
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RewardStat:
    reward_name: str
    reward_unit: str
    total_value: float


class UserNotAuthorizedError(Exception):
    """Пользователь не авторизован в Todoist."""


class StatisticsService:
    @staticmethod
    def _get_period_dates(period_key: str) -> tuple[datetime, datetime]:
        days = TodoistConfig.PERIOD_MAP.get(period_key)
        if not days:
            raise ValueError(f"Период не поддерживается: {period_key}. Доступны: {', '.join(TodoistConfig.PERIOD_MAP.keys())}")
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        return start, end

    @staticmethod
    def get_user_reward_stats(telegram_user_id: int, period_key: str) -> List[RewardStat]:
        """Вернуть агрегированную статистику наград пользователя за период.

        Не возвращает ORM-модели, только DTO `RewardStat`.
        """
        start_dt, end_dt = StatisticsService._get_period_dates(period_key)

        # Получаем пользователя и маппинг связок наград с тегами
        with SessionLocal() as db:
            user: User | None = (
                db.query(User).filter(User.telegram_id == telegram_user_id).first()
            )

            if not user or not getattr(user, "todoist_token", None):
                raise UserNotAuthorizedError(
                    "Пользователь не авторизован в Todoist"
                )

            reward_links = (
                db.query(RewardLink)
                .filter(RewardLink.user_id == telegram_user_id)
                .all()
            )

            reward_map: Dict[int, list[tuple[int, float]]] = {}
            for link in reward_links:
                reward_map.setdefault(link.tag_id, []).append(
                    (link.reward_id, link.value)
                )

            todoist_token = user.todoist_token

        # Внешние запросы к Todoist через единый клиент
        client = TodoistClient(todoist_token)
        completed_tasks = client.get_completed_tasks(start_dt, end_dt)
        tags = client.get_labels()

        name_to_tag_id = {tag.name: tag.id for tag in tags}

        # Подсчёт статистики по reward_id
        stats_by_reward: Dict[int, float] = {}
        for task in completed_tasks:
            labels = getattr(task, "labels", [])
            tag_ids = [
                name_to_tag_id[label]
                for label in labels
                if label in name_to_tag_id
            ]
            for tag_id in tag_ids:
                links = reward_map.get(int(tag_id), [])
                for reward_id, value in links:
                    stats_by_reward.setdefault(reward_id, 0.0)
                    stats_by_reward[reward_id] += value

        if not stats_by_reward:
            return []

        # Подтягиваем имена наград по ID и формируем DTO
        with SessionLocal() as db:
            rewards = (
                db.query(Reward)
                .filter(Reward.id.in_(stats_by_reward.keys()))
                .all()
            )

        rewards_by_id: Dict[int, Reward] = {r.id: r for r in rewards}

        result: List[RewardStat] = []
        for reward_id, total in stats_by_reward.items():
            reward = rewards_by_id.get(reward_id)
            if not reward:
                # Пропускаем «битые» записи
                continue
            result.append(
                RewardStat(
                    reward_name=reward.name,
                    reward_unit=reward.unit,
                    total_value=float(total),
                )
            )

        return result
