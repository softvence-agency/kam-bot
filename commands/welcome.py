from telegram import Update
from telegram.ext import ContextTypes

async def welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = await context.bot.get_me()
    bot_id = bot.id

    if not update.message or not update.message.new_chat_members:
        return

    for member in update.message.new_chat_members:
        if member.id == bot_id:
            await update.message.reply_text(
                "👋 Hello everyone!\n\n"
                "I’m *Softvence Omega KAM Bot*, here to help manage updates across teams.\n\n"
                "Here’s what you can do:\n\n"
                "• /timeline [Client Name] → Get client timeline\n"
                "• /update (optional message) → Send update to central group\n"
                "• /cupdate (optional message) → Send update to custom central group\n"
                "• /wupdate (optional message) → Send update to WixBuddy group\n\n"
                "💡 Tip: You can also *reply to any message* with these commands.\n\n"
                "🚀 Built by Foysal\n"
                "🤝 Last Contributed by Sabbir",
                parse_mode="Markdown"
            )