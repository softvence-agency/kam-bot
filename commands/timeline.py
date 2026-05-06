import logging
from html import escape
from datetime import datetime
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from core.config import API_BASE_URL

logger = logging.getLogger(__name__)


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
            response = await client.get(url)

        logger.info(
            f"✅ API response: {response.status_code} {response.reason_phrase}")
        logger.info(f"🔗 Final URL: {response.url}")

        if response.status_code == 200:
            data_list = response.json()
            if not isinstance(data_list, list) or not data_list:
                await update.message.reply_text(
                    f"⚠️ No data found for <code>{escape(client_name)}</code>.",
                    parse_mode="HTML"
                )
                return

            for i, data in enumerate(data_list, start=1):
                deli_time_raw = data.get('Deli_Last_Time')
                try:
                    dt = datetime.strptime(
                        deli_time_raw, "%Y-%m-%dT%H:%M:%S.%fZ")
                    deli_time_str = dt.strftime("%B %d, %Y %H:%M UTC")
                except:
                    deli_time_str = deli_time_raw or "N/A"

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
            await update.message.reply_text(
                f"❌ No data found for <code>{escape(client_name)}</code> (Status code: {response.status_code})",
                parse_mode="HTML"
            )

    except Exception as e:
        logger.exception("Unexpected exception occurred in /timeline")
        await update.message.reply_text("⚠️ An unexpected error occurred while fetching client data.")
