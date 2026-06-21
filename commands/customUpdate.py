import logging
from html import escape
from telegram import Update
from telegram.ext import ContextTypes
from core.config import CUSTOM_TARGET_GROUP_CHAT_ID

logger = logging.getLogger(__name__)

async def custom_update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Full command text (with @bot if exists)
    raw_text = update.message.text or ""
    text_html = update.message.text_html or ""
    # Remove command part
    parts = text_html.split(None, 1)
    content_to_send = parts[1] if len(parts) > 1 else ""

    # If no text → check reply
    if not content_to_send and update.message.reply_to_message:
        content_to_send = (
            update.message.reply_to_message.text_html
            or update.message.reply_to_message.caption_html
            or ""
        )

    # Metadata
    user = update.effective_user
    chat = update.effective_chat

    username = user.username or user.full_name
    chat_title = chat.title or "Private Chat"
    
    logger.info(f"Command /cupdate called by {username} in {chat_title} (ID: {chat.id})")

    if not content_to_send:
        content_to_send = f"{escape(raw_text)} {escape(username)}\n\n— {escape(chat_title)}"
    else:
        content_to_send += f"\n\n— <b>caller {escape(username)}</b> from <i>{escape(chat_title)}</i>"

    try:
        await context.bot.send_message(
            chat_id=CUSTOM_TARGET_GROUP_CHAT_ID,
            text=content_to_send,
            parse_mode="HTML"
        )

        logger.info(f"Successfully sent /cupdate from {username} to CUSTOM_TARGET_GROUP_CHAT_ID: {CUSTOM_TARGET_GROUP_CHAT_ID}")
        await update.message.reply_text(
            "✅ Your Update has been sent to the custom central update group."
        )

    except Exception as e:
        logger.error(f"Failed to send /cupdate from {username}: {e}")
        await update.message.reply_text(f"❌ Failed to send message: {e}")