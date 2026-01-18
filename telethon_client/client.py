from telethon import TelegramClient
from bot.config import API_ID, API_HASH, EXTERNAL_BOT

# Create Telethon client
client = TelegramClient("user_session", API_ID, API_HASH)

async def start_client():
    # Starts the client, logs in if needed
    await client.start()  # Will ask for phone + code on first run
    print("✅ Telethon user client started")

from telethon import events
from datetime import datetime

from telethon import events
from bot.config import EXTERNAL_BOT

@client.on(events.NewMessage(chats=EXTERNAL_BOT))
async def debug_external_bot(event):
    inspect_message(event.message)

