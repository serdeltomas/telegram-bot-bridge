# ----------------------------
# Core Functions
# ----------------------------
import asyncio
import re
from telethon import events
from telethon_client.client import client
from bot.config import EXTERNAL_BOT
from pathlib import Path

import random
from telethon.tl.functions.messages import StartBotRequest
from telethon.tl.types import InputPeerUser

_bot_started_cache = set()

async def ensure_bot_started(client, bot_username: str):
    if bot_username in _bot_started_cache:
        return

    bot = await client.get_entity(bot_username)

    await client(StartBotRequest(
        bot=bot,
        peer=InputPeerUser(client._self_id, client._self_access_hash),
        start_param="start",
        random_id=random.randint(1, 2**63 - 1)
    ))

    _bot_started_cache.add(bot_username)


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

    # debug
    await ensure_bot_started(client, "MusicsHuntersbot")
    await client.send_message("MusicsHuntersbot", song_name)


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
