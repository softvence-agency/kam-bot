import os
import httpx
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)
from html import escape
from datetime import datetime

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Google Apps Script API Endpoint
API_BASE_URL = os.getenv("API_BASE_URL")

# Handle /timeline command
async def timeline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    is_group = chat.type in ["group", "supergroup"]

    client_name = None

    if context.args:
        if context.args[0].lower() != "direct":
            client_name = context.args[0].strip()
        else:
            if is_group:
                group_title = chat.title or ""
                logger.info(f"Group title: {group_title}")
                if "||" in group_title:
                    client_name = group_title.split("||")[0].strip()
                else:
                    await update.message.reply_text(
                        "⚠️ Could not extract client name from the group title. Make sure it contains '||'."
                    )
                    return
            else:
                await update.message.reply_text(
                    "⚠️ The 'direct' option works only in group chats with properly formatted titles."
                )
                return
    else:
        if is_group:
            group_title = chat.title or ""
            logger.info(f"Group title: {group_title}")
            if "||" in group_title:
                client_name = group_title.split("||")[0].strip()
            else:
                await update.message.reply_text(
                    "⚠️ Could not extract client name from the group title. Make sure it contains '||'."
                )
                return
        else:
            await update.message.reply_text(
                "⚠️ Please provide the client name after the command, "
                "or use /timeline direct in a properly named group."
            )
            return

    url = f"{API_BASE_URL}?client={client_name}"
    logger.info(f"🔍 Fetching data for client: {client_name}")
    await update.message.reply_text(
        f"⏳ Fetching timeline for <code>{escape(client_name)}</code>...",
        parse_mode="HTML"
    )

    try:
        async with httpx.AsyncClient(timeout=100.0, follow_redirects=True) as client:
            headers = {"Accept": "application/json"}
            response = await client.get(url, headers=headers)

        logger.info(
            f"✅ API response: {response.status_code} {response.reason_phrase}")
        logger.info(f"🔗 Final URL: {response.url}")

        if response.status_code == 200:
            try:
                data_list = response.json()
            except Exception as json_error:
                logger.error(f"❌ JSON decoding failed: {json_error}")
                logger.error(
                    f"⚠️ Response content (text): {response.text[:500]}")
                await update.message.reply_text("🚫 API did not return valid JSON.")
                return

            if not isinstance(data_list, list) or not data_list:
                await update.message.reply_text(
                    f"⚠️ No data found for <code>{escape(client_name)}</code>.",
                    parse_mode="HTML"
                )
                return

            for i, data in enumerate(data_list, start=1):
                deli_time_raw = data.get('Deli_Last_Time')
                if deli_time_raw:
                    try:
                        dt = datetime.strptime(
                            deli_time_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
                        deli_time_str = dt.strftime("%B %d, %Y %H:%M UTC")
                    except Exception:
                        deli_time_str = deli_time_raw
                else:
                    deli_time_str = "N/A"

                message_text = (
                    f"📦 <b>Order #{i}</b>\n"
                    f"• <b>Client Name:</b> {escape(data.get('Client Name', 'N/A'))}\n"
                    f"• <b>Profile Name:</b> {escape(data.get('Profile Name', 'N/A'))}\n"
                    f"• <b>Deli Last Time:</b> {escape(deli_time_str)}\n"
                    f"• <b>Order ID:</b> {escape(data.get('Order ID', 'N/A'))}\n"
                    f"• <b>Status:</b> {escape(data.get('Status', 'N/A'))}\n"
                    f"• <b>Team Members:</b> {escape(data.get('Team Members', 'N/A'))}"
                )

                await update.message.reply_text(message_text, parse_mode="HTML")

        else:
            logger.warning(
                f"⚠️ Unexpected status code: {response.status_code}")
            await update.message.reply_text(
                f"❌ No data found for <code>{escape(client_name)}</code> (Status code: {response.status_code})",
                parse_mode="HTML"
            )

    except httpx.RequestError as e:
        logger.error(f"🌐 HTTPX Request error: {e}")
        await update.message.reply_text(
            f"🚫 Connection error: <code>{escape(str(e))}</code>",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.exception("❗ Unexpected exception occurred")
        await update.message.reply_text("⚠️ An unexpected error occurred while fetching client data.")

# Error handler


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception occurred:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text("⚠️ An internal error occurred on timeline command.")

# Main runner
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("timeline", timeline_command))
    app.add_error_handler(error_handler)

    logger.info("🤖 Bot is running...")
    app.run_polling()
