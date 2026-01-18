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

    # Send search query
    await client.send_message(EXTERNAL_BOT, song_name)

    try:
        # Wait for the first media (audio/document)
        media_msg = await asyncio.wait_for(media_future, timeout=timeout)

        # Determine filename
        filename = selected_filename or "Unknown.mp3"
        await media_msg.download_media(file=f"{download_path}/{filename}")
        print(f">>> Downloaded: {filename}")
        return filename

    except asyncio.TimeoutError:
        print(">>> Timeout waiting for media")
        return None

    finally:
        client.remove_event_handler(handler)


# ----------------------------
# Download by message ID
# ----------------------------
async def download_audio(message_id: int, path: str):
    """Download a specific audio or document message by message_id."""
    async for msg in client.iter_messages(EXTERNAL_BOT, ids=message_id):
        filename = "Unknown.mp3"

        if msg.audio:
            performer = getattr(msg.audio, "performer", None)
            title = getattr(msg.audio, "title", None)
            if performer and title:
                filename = f"{performer} - {title}.mp3"
            elif title:
                filename = f"{title}.mp3"
            await msg.download_media(file=f"{path}/{filename}")
            return filename

        elif msg.document:
            performer, title = None, None
            if msg.document.attributes:
                for attr in msg.document.attributes:
                    if isinstance(attr, DocumentAttributeAudio):
                        performer = getattr(attr, "performer", None)
                        title = getattr(attr, "title", None)
                        break
            if performer and title:
                filename = f"{performer} - {title}.mp3"
            elif title:
                filename = f"{title}.mp3"
            elif hasattr(msg.document, "file_name") and msg.document.file_name:
                filename = msg.document.file_name

            await msg.download_media(file=f"{path}/{filename}")
            return filename

    return None

# ----------------------------
# Download latest file (fallback)
# ----------------------------
async def download_latest_file(filename: str, path: str):
    """Download the latest file from the external bot."""
    async for msg in client.iter_messages(EXTERNAL_BOT, limit=1):
        if msg.file:
            await msg.download_media(file=f"{path}/{filename}")
            return True
    return False
