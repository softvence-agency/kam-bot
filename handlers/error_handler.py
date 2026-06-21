import logging
import json
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    if isinstance(update, Update):
        logger.error(f"Update that caused the error: {update.to_dict()}")
        if update.message:
            await update.message.reply_text("⚠️ An internal error occurred.")
