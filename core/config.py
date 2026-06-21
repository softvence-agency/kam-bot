import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")  # Add this in your .env file
PROXY_URL = os.getenv("PROXY_URL")  # Add this to .env if your VPS blocks Telegram
WIX_TARGET_GROUP_CHAT_ID = int(os.getenv("WIX_TARGET_GROUP_CHAT_ID") or 0)
WEBFLOW_TARGET_GROUP_CHAT_ID = int(os.getenv("WEBFLOW_TARGET_GROUP_CHAT_ID") or 0)
CUSTOM_TARGET_GROUP_CHAT_ID = int(os.getenv("CUSTOM_TARGET_GROUP_CHAT_ID") or 0)

TARGET_GROUP_CHAT_ID = int(os.getenv("TARGET_GROUP_CHAT_ID") or 0)