from typing import Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, CallbackContext, filters
)
from ..api.todoist_client import TodoistClient
from ..services.todoist import TodoistService
from ..services.reward_links import RewardLinkService
from ..services.rewards import RewardService, RewardDTO
from ..utils.auth import check_auth
from ..utils.logger import get_logger
from ..utils.texts import Messages

logger = get_logger(__name__)

AWAITING_REWARD_NAME, AWAITING_REWARD_UNIT, SELECTING_REWARD, SELECTING_TAG, AWAITING_REWARD_VALUE, EDIT_SELECT_REWARD, EDIT_SELECT_TAG, EDIT_AWAITING_VALUE, EDIT_AWAITING_ACTION = range(9)

# ----- Блок создания награды -----
async def start_create_reward(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    logger.info("Начало создания награды", user_id=user_id)
    await update.message.reply_text(Messages.REWARD_CREATE_START)
    context.user_data['reward_flow'] = {}
    return AWAITING_REWARD_NAME

async def process_reward_name(update: Update, context: CallbackContext) -> int:
    reward_name = update.message.text.strip()
    context.user_data['reward_flow']['name'] = reward_name
    await update.message.reply_text(Messages.reward_name_confirmed(reward_name))
    return AWAITING_REWARD_UNIT

async def complete_reward_creation(update: Update, context: CallbackContext) -> int:
    reward_flow = context.user_data.get('reward_flow', {})
    unit = update.message.text.strip()
    name = reward_flow.get('name')
    if not name:
        await update.message.reply_text(Messages.REWARD_NAME_NOT_FOUND)
        return ConversationHandler.END
    try:
        reward: RewardDTO = RewardService.create_reward(
            user_id=update.effective_user.id,
            name=name,
            unit=unit
        )
        await update.message.reply_text(Messages.reward_created(reward.name, reward.unit))
        logger.info("Награда создана", user_id=update.effective_user.id, reward_id=reward.id, reward_name=reward.name)
    except Exception as e:
        logger.exception("Ошибка при создании награды", error=str(e), user_id=update.effective_user.id)
        await update.message.reply_text(Messages.REWARD_CREATE_ERROR)
    finally:
        context.user_data.pop('reward_flow', None)
    return ConversationHandler.END

async def cancel_creation(update: Update, context: CallbackContext) -> int:
    user_id = update.effective_user.id
    logger.info("Отмена создания награды", user_id=user_id)
    await update.message.reply_text(Messages.REWARD_CREATE_CANCELED)
    context.user_data.pop('reward_flow', None)
    return ConversationHandler.END

# ------ Привязка награды к тегу ------
async def start_set_reward(update: Update) -> int:
    try:
        user_id = update.effective_user.id
        logger.info("Начало привязки награды к тегу", user_id=user_id)
        rewards: list[RewardDTO] = RewardService.get_user_rewards(user_id)
        if not rewards:
            logger.info("Нет наград для привязки", user_id=user_id)
            await update.message.reply_text(Messages.REWARD_NO_REWARDS)
            return ConversationHandler.END

        keyboard = [
            [InlineKeyboardButton(f"{r.name} ({r.unit})", callback_data=f"reward_{r.id}")]
            for r in rewards
        ]
        await update.message.reply_text(Messages.REWARD_SELECT_FOR_LINK, reply_markup=InlineKeyboardMarkup(keyboard))
        return SELECTING_REWARD
    except Exception as e:
        logger.exception("Ошибка получения наград", error=str(e), user_id=update.effective_user.id)
        await update.message.reply_text(Messages.REWARD_ERROR_GETTING)
        return ConversationHandler.END

async def select_tag_for_reward(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    try:
        user_id = update.effective_user.id
        reward_id = int(query.data.split("_")[1])
        logger.info("Выбрана награда для привязки", user_id=user_id, reward_id=reward_id)
        context.user_data.setdefault("reward_flow", {})["reward_id"] = reward_id
        user = TodoistService.get_user_by_telegram_id(user_id)
        if not await check_auth(update, user):
            return ConversationHandler.END
        client = TodoistClient(user.todoist_token)
        tags = client.get_labels()
        if not tags:
            logger.info("У пользователя нет тегов для привязки", user_id=user_id, reward_id=reward_id)
            await query.edit_message_text(Messages.REWARD_NO_TAGS)
            return ConversationHandler.END

        keyboard = [
            [InlineKeyboardButton(tag.name, callback_data=f"tag_{tag.id}")]
            for tag in tags
        ]
        await query.edit_message_text(Messages.REWARD_SELECT_TAG, reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info("Список тегов для выбора отправлен", user_id=user_id, reward_id=reward_id, tags_count=len(tags))
        return SELECTING_TAG
    except Exception as e:
        logger.exception("Ошибка при выборе тега", error=str(e), user_id=update.effective_user.id)
        await query.edit_message_text(Messages.REWARD_SELECT_TAG_ERROR)
        return ConversationHandler.END

async def set_reward_value(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    tag_id = query.data.split("_")[1]
    reward_id = context.user_data.setdefault("reward_flow", {}).get("reward_id")
    logger.info("Выбран тег для привязки награды", user_id=user_id, reward_id=reward_id, tag_id=tag_id)
    context.user_data["reward_flow"]["tag_id"] = tag_id
    await query.edit_message_text(Messages.REWARD_ENTER_VALUE)
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
            logger.warning("Некорректное значение награды", user_id=user_id, reward_id=reward_id, tag_id=tag_id, input_text=update.message.text)
            await update.message.reply_text(Messages.REWARD_INVALID_VALUE)
            return AWAITING_REWARD_VALUE

        if RewardLinkService.find_existing_link(user_id, reward_id, tag_id):
            logger.info("Награда уже привязана к тегу", user_id=user_id, reward_id=reward_id, tag_id=tag_id)
            await update.message.reply_text(Messages.REWARD_ALREADY_LINKED)
            return ConversationHandler.END
        RewardLinkService.create_link(
            user_id=user_id, reward_id=reward_id, tag_id=tag_id, value=value
        )
        await update.message.reply_text(Messages.REWARD_LINKED_SUCCESS)
        logger.info("Награда привязана к тегу", user_id=user_id, reward_id=reward_id, tag_id=tag_id, value=value)
    except Exception as e:
        logger.exception("Ошибка при сохранении связи награды с тегом", error=str(e), user_id=user_id, reward_id=reward_id, tag_id=tag_id)
        await update.message.reply_text(Messages.REWARD_SAVE_ERROR)
    finally:
        context.user_data.pop('reward_flow', None)
    return ConversationHandler.END

async def show_user_rewards(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.effective_user.id
        logger.info("Запрос списка наград", user_id=user_id)
        rewards: list[RewardDTO] = RewardService.get_user_rewards(user_id)
        if not rewards:
            logger.info("У пользователя нет наград", user_id=user_id)
            await update.message.reply_text(Messages.REWARDS_NONE)
            return
        message = Messages.REWARDS_LIST_HEADER + "".join(
            Messages.rewards_item(r.name, r.unit) for r in rewards
        )
        await update.message.reply_text(message)
        logger.info("Список наград отправлен", user_id=user_id, rewards_count=len(rewards))
    except Exception as e:
        logger.exception("Ошибка вывода наград", error=str(e), user_id=update.effective_user.id)
        await update.message.reply_text(Messages.REWARDS_LIST_ERROR)



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
