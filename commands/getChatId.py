from telegram import Update
from telegram.ext import ContextTypes


async def getId_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(f"Chat ID: {chat_id}")  # For debugging purposes
    await update.message.reply_text(f"Group chat ID is: {chat_id}")
