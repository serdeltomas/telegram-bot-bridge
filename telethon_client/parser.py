from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest
from telethon.tl.types import DocumentAttributeAudio
from bot.config import EXTERNAL_BOT, client
import os

async def query_external_bot(song_name: str):
    """Send query to @fmusbot and return inline button options."""
    await client.send_message(EXTERNAL_BOT, song_name)

    # Wait for the bot to respond with inline buttons
    async for msg in client.iter_messages(EXTERNAL_BOT, limit=5):
        if msg.reply_markup and msg.reply_markup.rows:
            # Flatten buttons
            buttons = [b for row in msg.reply_markup.rows for b in row.buttons]
            options = [{"title": b.text, "data": b.data, "msg_id": msg.id} for b in buttons]
            return options

    return []

async def download_audio_from_selection(msg_id: int, button_data: bytes, download_path: str):
    """Click the button, wait for audio, download it."""
    # Simulate pressing the button
    await client(GetBotCallbackAnswerRequest(peer=EXTERNAL_BOT, msg_id=msg_id, data=button_data))

    # Wait for the bot to send audio
    async for msg in client.iter_messages(EXTERNAL_BOT, limit=5):
        # Audio messages
        if msg.audio:
            filename = f"{msg.audio.performer or 'Unknown'} - {msg.audio.title or 'Unknown'}.mp3"
            path = os.path.join(download_path, filename)
            await msg.download_media(file=path)
            return path
        # Audio as document
        elif msg.document:
            for attr in msg.document.attributes:
                if isinstance(attr, DocumentAttributeAudio):
                    filename = f"{attr.performer or 'Unknown'} - {attr.title or 'Unknown'}.mp3"
                    path = os.path.join(download_path, filename)
                    await msg.download_media(file=path)
                    return path

    return None
