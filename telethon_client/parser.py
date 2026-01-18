# ----------------------------
# Core Functions
# ----------------------------
import asyncio
import re
from telethon import events
from telethon_client.client import client
from bot.config import EXTERNAL_BOT
from pathlib import Path

def clean_filename(name: str) -> str:
    name = re.sub(r'^\d+\.\s*', '', name)

    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip()

    p = Path(name)
    if not p.suffix:
        name += ".mp3"

    return name

async def query_external_bot_first(song_name: str, download_path: str, timeout=30):
    """Send a query to the external bot and download the first audio received."""
    media_future = asyncio.get_running_loop().create_future()
    selected_filename = None

    async def handler(event):
        nonlocal selected_filename
        msg = event.message

        # If this is a menu with buttons
        if msg.reply_markup:
            first_row = msg.reply_markup.rows[0]
            btn = first_row.buttons[0]
            if hasattr(btn, "data") and btn.data.startswith(b"dl:"):
                selected_filename = clean_filename(btn.text)
                await asyncio.sleep(1.5)
                await msg.click(0)

        # If this is audio or document
        if (msg.audio or msg.document) and not media_future.done():
            media_future.set_result(msg)

    client.add_event_handler(handler, events.NewMessage(chats=EXTERNAL_BOT))
