import logging
from typing import Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, CallbackContext, filters
)
from ..services.todoist import TodoistService
from ..api.labels import get_labels
from ..services.reward_links import RewardLinkService
from ..services.rewards import RewardService

logger = logging.getLogger(__name__)

AWAITING_REWARD_NAME, AWAITING_REWARD_UNIT, SELECTING_REWARD, SELECTING_TAG, AWAITING_REWARD_VALUE, EDIT_SELECT_REWARD, EDIT_SELECT_TAG, EDIT_AWAITING_VALUE, EDIT_AWAITING_ACTION = range(9)

# ----- Блок создания награды -----
async def start_create_reward(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Создаем новую награду!\nВведите название (например: 'Очки опыта'):")
    context.user_data['reward_flow'] = {}
    return AWAITING_REWARD_NAME

async def process_reward_name(update: Update, context: CallbackContext) -> int:
    reward_name = update.message.text.strip()
    context.user_data['reward_flow']['name'] = reward_name
    await update.message.reply_text(f"Название: {reward_name}\nТеперь введите единицы измерения (например: 'раз'):")
    return AWAITING_REWARD_UNIT

async def complete_reward_creation(update: Update, context: CallbackContext) -> int:
    reward_flow = context.user_data.get('reward_flow', {})
    unit = update.message.text.strip()
    name = reward_flow.get('name')
    if not name:
        await update.message.reply_text("❌ Не найдено название награды")
        return ConversationHandler.END
    try:
        reward = RewardService.create_reward(
            user_id=update.effective_user.id,
            name=name,
            unit=unit
        )
        await update.message.reply_text(f"🎉 Награда создана!\n{reward.name} ({reward.unit})")
    except Exception as e:
        logger.error("Reward creation error: %s", e)
        await update.message.reply_text("❌ Ошибка при создании")
    finally:
        context.user_data.pop('reward_flow', None)
    return ConversationHandler.END

async def cancel_creation(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Создание награды отменено.")
    context.user_data.pop('reward_flow', None)
    return ConversationHandler.END

# ------ Привязка награды к тегу ------
async def start_set_reward(update: Update) -> int:
    try:
        rewards = RewardService.get_user_rewards(update.effective_user.id)
        if not rewards:
            await update.message.reply_text("❌ У вас нет наград. Создайте через /newreward")
            return ConversationHandler.END

        keyboard = [
            [InlineKeyboardButton(f"{r.name} ({r.unit})", callback_data=f"reward_{r.id}")]
            for r in rewards
        ]
        await update.message.reply_text("Выберите награду для привязки:", reply_markup=InlineKeyboardMarkup(keyboard))
        return SELECTING_REWARD
    except Exception as e:
        logger.error("Error fetching rewards: %s", e)
        await update.message.reply_text("Ошибка получения наград.")
        return ConversationHandler.END

async def select_tag_for_reward(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    try:
        reward_id = int(query.data.split("_")[1])
        context.user_data.setdefault("reward_flow", {})["reward_id"] = reward_id
        user = TodoistService.get_user_by_telegram_id(update.effective_user.id)
        tags = get_labels(user.todoist_token)
        if not tags:
            await query.edit_message_text("❌ У вас нет тегов в Todoist")
            return ConversationHandler.END

        keyboard = [
            [InlineKeyboardButton(tag.name, callback_data=f"tag_{tag.id}")]
            for tag in tags
        ]
        await query.edit_message_text("Выберите тег для привязки:", reply_markup=InlineKeyboardMarkup(keyboard))
        return SELECTING_TAG
    except Exception as e:
        logger.error("Error during tag selection: %s", e)
        await query.edit_message_text("Произошла ошибка при выборе тега.")
        return ConversationHandler.END

async def set_reward_value(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    tag_id = query.data.split("_")[1]
    context.user_data.setdefault("reward_flow", {})["tag_id"] = tag_id
    await query.edit_message_text("Введите, сколько единиц награды давать за этот тег (например, 1.5):")
    return AWAITING_REWARD_VALUE

async def save_reward_link(update: Update, context: CallbackContext) -> int:
    reward_flow = context.user_data.get("reward_flow", {})
    try:
        tag_id = reward_flow.get('tag_id')
        reward_id = reward_flow.get('reward_id')
        user_id = update.effective_user.id
        try:
            value = float(update.message.text)
        except Exception:
            await update.message.reply_text("❌ Пожалуйста, введите число (например: 1.5)")
            return AWAITING_REWARD_VALUE

        if RewardLinkService.find_existing_link(user_id, reward_id, tag_id):
            await update.message.reply_text(
                "⚠️ Эта награда уже привязана к тегу\n"
            )
            return ConversationHandler.END
        RewardLinkService.create_link(
            user_id=user_id, reward_id=reward_id, tag_id=tag_id, value=value
        )
        await update.message.reply_text("✅ Награда привязана к тегу!")
    except Exception as e:
        logger.error("Error saving reward link: %s", e)
        await update.message.reply_text("❌ Ошибка при сохранении")
    finally:
        context.user_data.pop('reward_flow', None)
    return ConversationHandler.END

async def show_user_rewards(update: Update, context: CallbackContext) -> None:
    try:
        rewards = RewardService.get_user_rewards(update.effective_user.id)
        if not rewards:
            await update.message.reply_text("У вас пока нет наград. Создайте через /newreward")
            return
        message = "🎁 Добавленные награды:\n" + "".join(
            f"\n• {r.name} ({r.unit})" for r in rewards
        )
        await update.message.reply_text(message)
    except Exception as e:
        logger.error("Error showing user rewards: %s", e)
        await update.message.reply_text("Ошибка вывода наград.")



# ---- Handlers ---- 
def get_rewards_handlers() -> list:
    return [
        ConversationHandler(
            entry_points=[CommandHandler('newreward', start_create_reward)],
            states={
                AWAITING_REWARD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_reward_name)],
                AWAITING_REWARD_UNIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, complete_reward_creation)],
            },
            fallbacks=[CommandHandler('cancel', cancel_creation)],
            allow_reentry=True
        ),
        ConversationHandler(
            entry_points=[CommandHandler('setreward', select_tag_for_reward)],
            states={
                SELECTING_REWARD: [CallbackQueryHandler(select_tag_for_reward, pattern=r'^reward_\d+$')],
                SELECTING_TAG: [CallbackQueryHandler(set_reward_value, pattern=r'^tag_\d+$')],
                AWAITING_REWARD_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_reward_link)],
            },
            fallbacks=[CommandHandler("cancel", cancel_creation)]
        ),
        CommandHandler("rewards", show_user_rewards),
    ]
