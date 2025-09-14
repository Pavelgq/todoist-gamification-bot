

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import SessionLocal
from ..models import User
from ..api.todoist_api import TodoistHelper

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
      user = update.effective_user
      logger.info(f"User {user.id} started the bot")

      db = SessionLocal()
      try:
          db_user = db.query(User).filter(User.telegram_id == user.id).first()
          
          if db_user and db_user.todoist_token:
              await update.message.reply_text("Вы уже авторизованы в Todoist!")
          else:
              state = str(user.id)
              auth_url = TodoistHelper.get_auth_url(state)
              
              await update.message.reply_text(
                  "Пожалуйста, авторизуйте доступ к вашему Todoist аккаунту:",
                  reply_markup=InlineKeyboardMarkup([
                      [InlineKeyboardButton("Авторизовать Todoist", url=auth_url)]
                  ])
              )
      finally:
          db.close()

    except Exception as e:
      logger.error(f"Error in start: {e}", exc_info=True)
      await update.message.reply_text("Произошла ошибка при обработке команды")