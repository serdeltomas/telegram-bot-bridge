import asyncio
from telethon_client.client import client
from bot.config import EXTERNAL_BOT


async def query_external_bot(song_name: str):
    """Send song query to @fmusbot and collect audio options."""
    # send the query to the external bot
    await client.send_message(EXTERNAL_BOT, song_name)

    options = []
    async for msg in client.iter_messages(EXTERNAL_BOT, limit=10):
        if msg.audio:
            options.append({
                "id": msg.id,
                "title": msg.audio.title or "Unknown",
                "performer": msg.audio.performer or "Unknown",
                "duration": msg.audio.duration
            })
        elif msg.document and msg.document.mime_type.startswith("audio"):
            # Some bots send audio as document
            options.append({
                "id": msg.id,
                "title": msg.document.attributes[0].title if msg.document.attributes else "Unknown",
                "performer": msg.document.attributes[0].performer if msg.document.attributes else "Unknown",
                "duration": msg.document.attributes[0].duration if msg.document.attributes else 0
            })
    
    if not options:
        return "❌ No audio found"
    return options



async def download_audio(message_id: int, path: str):
    """Download a specific audio message by message_id."""
    async for msg in client.iter_messages(EXTERNAL_BOT, ids=message_id):
        if msg.audio:
            filename = f"{msg.audio.performer} - {msg.audio.title}.mp3"
            await msg.download_media(file=f"{path}/{filename}")
            return filename
    return None


async def download_latest_file(filename: str, path: str):
    """Download the latest file from the external bot."""
    async for msg in client.iter_messages(EXTERNAL_BOT, limit=1):
        if msg.file:
            await msg.download_media(file=f"{path}/{filename}")
            return True
    return False
