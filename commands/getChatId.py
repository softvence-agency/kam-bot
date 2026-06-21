import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def getId_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    username = user.username or user.full_name
    
    logger.info(f"Command /getid called by {username} in chat {update.effective_chat.title} (ID: {chat_id})")
    print(f"Chat ID: {chat_id}")  # For debugging purposes
    await update.message.reply_text(f"Group chat ID is: {chat_id}")

