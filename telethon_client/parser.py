# ----------------------------
# Core Functions
# ----------------------------
import asyncio
import re
from telethon import events
from telethon_client.client import client
from bot.config import EXTERNAL_BOT

def clean_filename(name: str) -> str:
    """Clean string to be safe as a filename."""
    name = re.sub(r'^\d+\.\s*', '', name)  # remove "1. " prefix
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()

async def query_external_bot_first(song_name: str, download_path: str, timeout_menu=10, timeout_media=30):
    """Send query, click first track button, download media."""
    await client.send_message(EXTERNAL_BOT, song_name)

    menu_future = asyncio.get_running_loop().create_future()
    media_future = asyncio.get_running_loop().create_future()
    selected_filename = None

    @client.on(events.NewMessage(chats=EXTERNAL_BOT))
    async def menu_handler(event):
        nonlocal selected_filename
        msg = event.message
        if msg.reply_markup:
            # pick the first track button (skip navigation, filters)
            for row in msg.reply_markup.rows:
                btn = row.buttons[0]
                if hasattr(btn, "data") and btn.data.startswith(b"dl:"):
                    selected_filename = clean_filename(btn.text)
                    print(f">>> Clicking button: {selected_filename}")
                    # Proper click
                    await msg.click(0)
                    if not menu_future.done():
                        menu_future.set_result(msg)
                    return

    @client.on(events.NewMessage(chats=EXTERNAL_BOT))
    async def media_handler(event):
        msg = event.message
        if msg.audio or msg.document:
            if not media_future.done():
                media_future.set_result(msg)

    try:
        # Wait for menu to appear and click the button
        await asyncio.wait_for(menu_future, timeout=timeout_menu)
        # Wait for media to be sent
        media_msg = await asyncio.wait_for(media_future, timeout=timeout_media)

        filename = selected_filename or "Unknown.mp3"
        await media_msg.download_media(file=f"{download_path}/{filename}")
        print(f">>> Downloaded: {filename}")
        return filename

    except asyncio.TimeoutError:
        print(">>> Timeout waiting for menu or media")
        return None

    finally:
        client.remove_event_handler(menu_handler)
        client.remove_event_handler(media_handler)

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
