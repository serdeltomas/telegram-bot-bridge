from telethon import TelegramClient
from bot.config import API_ID, API_HASH

# Create Telethon client
client = TelegramClient("user_session", API_ID, API_HASH)

async def start_client():
    # Starts the client, logs in if needed
    await client.start()  # Will ask for phone + code on first run
    print("✅ Telethon user client started")
