from telegram import Update
from telegram.ext import ContextTypes

from ..config import TodoistConfig
from ..services.statistics import StatisticsService, UserNotAuthorizedError
from ..utils.logger import get_logger
from ..utils.texts import Messages

logger = get_logger(__name__)

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Хендлер для вывода статистики по закрытым задачам"""
    try:
        user_id = update.effective_user.id

        if context.args:
            period_key = context.args[0].lower()
        else:
            period_key = "неделя" 

        logger.info("Запрос статистики", user_id=user_id, period=period_key)
        stats = StatisticsService.get_user_reward_stats(user_id, period_key)

        if not stats:
            logger.info("Статистика пуста", user_id=user_id, period=period_key)
            await update.message.reply_text(Messages.stats_period_empty(period_key))
            return

        text = Messages.stats_period_header(period_key)
        for item in stats:
            text += Messages.stats_item(item.reward_name, item.reward_unit, item.total_value)

        await update.message.reply_text(text)
        logger.info("Статистика отправлена", user_id=user_id, period=period_key, items_count=len(stats))

        # TODO: (Опционально) добавить график или визуализацию

    except UserNotAuthorizedError:
        logger.warning("Попытка получить статистику без авторизации", user_id=user_id)
        await update.message.reply_text(Messages.AUTH_REQUIRED)
        return
    except Exception as e:
        logger.exception("Ошибка при подсчёте статистики", error=str(e), user_id=user_id, period=period_key)
        await update.message.reply_text(Messages.STATS_ERROR)