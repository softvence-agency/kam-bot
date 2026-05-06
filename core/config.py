import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")  # Add this in your .env file
WIX_TARGET_GROUP_CHAT_ID = int(os.getenv("WIX_TARGET_GROUP_CHAT_ID"))
WEBFLOW_TARGET_GROUP_CHAT_ID = int(os.getenv("WEBFLOW_TARGET_GROUP_CHAT_ID"))
CUSTOM_TARGET_GROUP_CHAT_ID = int(os.getenv("CUSTOM_TARGET_GROUP_CHAT_ID"))

TARGET_GROUP_CHAT_ID = int(os.getenv("TARGET_GROUP_CHAT_ID"))