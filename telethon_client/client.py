from telethon import TelegramClient
from bot.config import API_ID, API_HASH

client = TelegramClient('user_session', API_ID, API_HASH)

async def start_client():
    # user login
    await client.start()  # will ask for phone + code once
    print("✅ Telethon user client started")
