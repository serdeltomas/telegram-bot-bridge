from telethon import TelegramClient
from bot.config import API_ID, API_HASH

# Create Telethon client
client = TelegramClient("user_session", API_ID, API_HASH)

async def start_client():
    # Starts the client, logs in if needed
    await client.start()  # Will ask for phone + code on first run
    print("✅ Telethon user client started")

from telethon import events
from datetime import datetime

@client.on(events.NewMessage(chats=EXTERNAL_BOT))
async def debug_fmus_messages(event):
    m = event.message

    print("\n===== FMUS EVENT =====")
    print("Time:", datetime.utcnow().isoformat())
    print("ID:", m.id)
    print("Date:", m.date)
    print("Grouped ID:", m.grouped_id)
    print("Out:", m.out)
    print("Has audio:", bool(m.audio))
    print("Has document:", bool(m.document))
    print("Text:", repr(m.message))
    print("Reply markup:", bool(m.reply_markup))
    print("======================\n")
