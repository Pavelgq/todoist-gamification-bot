from datetime import datetime, timedelta, timezone
from ..api.todoist_api import TodoistHelper
from ..models import User, SessionLocal, RewardLink, Reward
from todoist_api_python.api import TodoistAPI
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from sqlalchemy.orm import joinedload
import logging

from ..utils.auth import check_auth

logger = logging.getLogger(__name__)

# Периоды в днях
PERIOD_MAP = {
    "неделя": 7,
    "месяц": 30,
    "3 месяца": 90,
}

def get_period_dates(period_key: str):
    """Вернуть дату начала и конца периода по ключу с tzinfo=UTC"""
    days = PERIOD_MAP.get(period_key)
    if not days:
        raise ValueError("Период не поддерживается")
    end = datetime.now(timezone.utc) 
    start = end - timedelta(days=days)
    return start, end

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хендлер для вывода статистики по закрытым задачам"""
    try:
        user_id = update.effective_user.id

        if context.args:
            period_key = context.args[0].lower()
        else:
            period_key = "неделя" 
        
        start_dt, end_dt = get_period_dates(period_key)
        
        with SessionLocal() as db:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not await check_auth(update, user):
                return
            
            reward_links = db.query(RewardLink).filter(
                RewardLink.user_id == user_id
            ).all()

            reward_map = {}
            for link in reward_links:
                reward_map.setdefault(link.tag_id, []).append((link.reward_id, link.value))

        completed_tasks = TodoistHelper.get_completed_tasks(user.todoist_token, start_dt, end_dt, logger)
        tags = TodoistHelper.get_labels(user.todoist_token, logger)
        print(tags)
        name_to_tag_id = {tag.name: tag.id for tag in tags}

        print(completed_tasks)
        stats_by_reward = {}

        for task in completed_tasks:
            labels = getattr(task, "labels", [])  # список строк, например ['ХЛТР']
            tag_ids = [name_to_tag_id[label] for label in labels if label in name_to_tag_id]
            for tag_id in tag_ids:
                links = reward_map.get(int(tag_id), [])
                for reward_id, value in links:
                    stats_by_reward.setdefault(reward_id, 0)
                    stats_by_reward[reward_id] += value

        if not stats_by_reward:
            await update.message.reply_text(f"Нет начисленных наград за период «{period_key}».")
            return

        with SessionLocal() as db:
            reward_names = {r.id: r for r in db.query(Reward).filter(Reward.id.in_(stats_by_reward.keys())).all()}
        text = f"🌟 Статистика за период «{period_key}»:\n\n"
        for reward_id, total in stats_by_reward.items():
            name = reward_names.get(reward_id)
            if name:
                text += f"• {name.name} ({name.unit}): {total:.2f}\n"
            else:
                text += f"• [reward {reward_id}]: {total:.2f}\n"

        await update.message.reply_text(text)

        # TODO: (Опционально) добавить график или визуализацию

    except Exception as e:
        logger.error(f"Ошибка show_stats: {e}", exc_info=True)
        await update.message.reply_text("Произошла ошибка при подсчёте статистики.")