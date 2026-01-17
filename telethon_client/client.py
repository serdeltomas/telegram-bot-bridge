from telethon import TelegramClient
from bot.config import API_ID, API_HASH, BOT_TOKEN

client = TelegramClient('user_session', API_ID, API_HASH)

async def start_client():
    # If using bot token
    await client.start(bot_token=BOT_TOKEN)
    print("✅ Telethon bot client started")
