import asyncio
import re
from datetime import datetime
from telethon import events, functions
from telethon.tl.types import DocumentAttributeAudio, KeyboardButtonCallback
from telethon_client.client import client
from bot.config import EXTERNAL_BOT

# ----------------------------
# Utilities
# ----------------------------
def clean_filename(name: str) -> str:
    """Clean string to be safe as a filename and strip duration prefix."""
    name = re.sub(r'^\d{1,2}:\d{2}\s*\|\s*', '', name)
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()

def debug_message_buttons(msg):
    """Print detailed info about the buttons of a message (for debugging)."""
    print("===== DEBUG BOT MENU =====")
    print(f"Message ID: {msg.id}")
    print(f"Text: {msg.text}")
    if msg.reply_markup:
        print("Reply markup present!")
        for row_index, row in enumerate(msg.reply_markup.rows):
            print(f"Row {row_index}:")
            for btn_index, btn in enumerate(row.buttons):
                if isinstance(btn, KeyboardButtonCallback):
                    print(f"  Button {btn_index}: text='{btn.text}', type={type(btn)}")
                    print(f"    callback data: {btn.data}")
                else:
                    print(f"  Button {btn_index}: text='{btn.text}', type={type(btn)}")
    else:
        print("No reply markup found.")
    print("===========================")

# ----------------------------
# Core Functions
# ----------------------------
async def query_external_bot_first(song_name: str, download_path: str, timeout_menu=10, timeout_media=20):
    """Send a query to the bot, select the first track, and download the media."""
    print(">>> Sending query:", song_name)
    await client.send_message(EXTERNAL_BOT, song_name)

    loop = asyncio.get_running_loop()
    future_menu = loop.create_future()
    future_media = loop.create_future()
    selected_filename = None
    selected_callback_data = None

    # ---- Event Handlers ----
    @client.on(events.NewMessage(chats=EXTERNAL_BOT))
    async def menu_handler(event):
        nonlocal selected_filename, selected_callback_data
        msg = event.message
        if msg.reply_markup:
            # Debug print all buttons
            debug_message_buttons(msg)

            # Select the first track-like button (skip "➡️", filters, etc.)
            for row in msg.reply_markup.rows:
                btn = row.buttons[0]
                if isinstance(btn, KeyboardButtonCallback) and btn.data.startswith(b'dl:'):
                    selected_filename = clean_filename(btn.text)
                    selected_callback_data = btn.data
                    if not future_menu.done():
                        future_menu.set_result(msg)
                    break

    @client.on(events.NewMessage(chats=EXTERNAL_BOT))
    async def media_handler(event):
        msg = event.message
        if msg.audio or msg.document:
            print(">>> Accepted media msg:", msg.id, msg.date.isoformat())
            if not future_media.done():
                future_media.set_result(msg)

    # ---- Wait for menu and send callback ----
    try:
        menu_msg = await asyncio.wait_for(future_menu, timeout=timeout_menu)
        if selected_callback_data:
            print(f">>> Clicking button: {selected_filename}")
            await client(
                functions.messages.GetBotCallbackAnswerRequest(
                    peer=EXTERNAL_BOT,
                    msg_id=menu_msg.id,
                    data=selected_callback_data
                )
            )
        else:
            print(">>> No track button found in menu")
            return None

        # Wait for the media message
        media_msg = await asyncio.wait_for(future_media, timeout=timeout_media)

        # Determine filename
        filename = f"{selected_filename}.mp3" if selected_filename else "Unknown.mp3"

        # Download the media
        await media_msg.download_media(file=f"{download_path}/{filename}")
        print(f">>> Downloaded as {filename}")
        return filename

    except asyncio.TimeoutError:
        print(">>> Timeout: Bot did not send menu or media")
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
