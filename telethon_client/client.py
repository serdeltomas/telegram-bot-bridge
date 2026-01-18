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

@client.on(events.NewMessage(chats=EXTERNAL_BOT))
async def menu_handler(event):
    m = event.message
    debug_message_buttons(m)

def debug_message_buttons(msg):
    print("===== DEBUG BOT MENU =====")
    print("Message ID:", msg.id)
    print("Text:", msg.text)
    if msg.reply_markup:
        print("Reply markup present!")
        for i, row in enumerate(msg.reply_markup.rows):
            print(f"Row {i}:")
            for j, button in enumerate(row.buttons):
                print(f"  Button {j}: text='{button.text}', type={type(button)}")
                if hasattr(button, "url"):
                    print(f"    URL: {button.url}")
                if hasattr(button, "data"):
                    print(f"    callback data: {button.data}")
    else:
        print("No reply markup.")
    print("===========================")

