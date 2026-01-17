import asyncio
from telethon_client.client import client
from bot.config import EXTERNAL_BOT
from telethon import functions, types, events, TelegramClient
from telethon.tl.types import Message
from datetime import datetime

async def query_external_bot_first(query: str, timeout: int = 10):
    """
    Send a query to the external bot and get the latest menu message.
    Returns the selected media message after clicking the first button.
    """
    print(f">>> Sending query: {query}")
    await client.send_message(EXTERNAL_BOT, query)

    # Wait for the new menu to arrive
    menu_future = asyncio.get_running_loop().create_future()

    @client.on(events.NewMessage(chats=EXTERNAL_BOT))
    async def menu_handler(event):
        msg: Message = event.message
        if msg.reply_markup:  # Only consider messages with buttons
            if not menu_future.done():
                print(f">>> New menu received, msg_id={msg.id}, buttons={len(msg.reply_markup.rows)}")
                menu_future.set_result(msg)

    try:
        menu_msg: Message = await asyncio.wait_for(menu_future, timeout=timeout)
    except asyncio.TimeoutError:
        print(">>> Timeout waiting for menu from bot")
        client.remove_event_handler(menu_handler)
        return None

    # Remove the temporary handler
    client.remove_event_handler(menu_handler)

    # Pick the first button (you can change this to pick specific song if needed)
    button = menu_msg.reply_markup.rows[0].buttons[0]
    print(f">>> Clicking first button: {button.text}")

    # Wait for the bot to respond with the audio/document
    media_future = asyncio.get_running_loop().create_future()

    @client.on(events.NewMessage(chats=EXTERNAL_BOT))
    async def media_handler(event):
        msg: Message = event.message
        if msg.media:
            if not media_future.done():
                print(f">>> Media received: msg_id={msg.id}, media_type={type(msg.media)}")
                media_future.set_result(msg)

    # Click the button (simulate user clicking)
    await menu_msg.click(0)  # Click first button, can adjust row/button index

    try:
        media_msg: Message = await asyncio.wait_for(media_future, timeout=timeout)
    except asyncio.TimeoutError:
        print(">>> Timeout waiting for media")
        client.remove_event_handler(media_handler)
        return None

    # Remove handler
    client.remove_event_handler(media_handler)

    return media_msg


async def download_audio(msg: Message):
    """
    Downloads audio from a message.
    Handles both Audio and Document types.
    """
    if msg.audio:
        filename = f"{msg.audio.performer or 'Unknown'} - {msg.audio.title or 'Unknown'}.mp3"
        path = await msg.download_media(file=filename)
        print(f">>> Audio downloaded to {path}")
        return path
    elif msg.document:
        filename = await msg.download_media()
        print(f">>> Document downloaded to {filename}")
        return filename
    else:
        print(">>> No audio/document found in message")
        return None
