import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from core.config import TELEGRAM_BOT_TOKEN, PROXY_URL
from commands.welcome import welcome_message 
from commands.timeline import timeline_command
from commands.update import update_command
from commands.wixbuddyupdate import wix_update_command
from commands.webflowUpdate import webflow_update_command
from commands.customUpdate import custom_update_command
from commands.getChatId import getId_command
from handlers.error_handler import error_handler

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN is not set. Please check your .env file.")
        exit(1)

    if PROXY_URL:
        builder = builder.proxy(PROXY_URL).get_updates_proxy(PROXY_URL)
        logger.info(f"Using proxy: {PROXY_URL}")
    else:
        builder = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN)
        
    app = builder.build()

    app.add_handler(
        MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_message)
    )
    app.add_handler(CommandHandler("timeline", timeline_command))
    app.add_handler(CommandHandler("update", update_command))
    app.add_handler(CommandHandler("cupdate", custom_update_command))
    app.add_handler(CommandHandler("wupdate", wix_update_command))
    app.add_handler(CommandHandler("getid", getId_command))
    app.add_handler(CommandHandler("wfupdate", webflow_update_command))

    # Add a message handler for private chats only
    app.add_handler(MessageHandler( filters.TEXT & filters.ChatType.PRIVATE, welcome_message))

    app.add_error_handler(error_handler)

    logger.info("🤖 Bot is running...")
    app.run_polling()
