import asyncio
from telethon_client.client import client
from bot.config import EXTERNAL_BOT


async def query_external_bot_first(song_name: str):
    """Send song query to @fmusbot and return the first file (audio or document)."""
    await client.send_message(EXTERNAL_BOT, song_name)

    async for msg in client.iter_messages(EXTERNAL_BOT, limit=10):
        # Debug: print full message object
        print("=== Received Message ===")
        print(msg.stringify())  # Telethon's built-in method for full inspection
        print("========================")

        if msg.audio:
            return {
                "file_id": msg.id,
                "title": getattr(msg.audio, "title", "Unknown"),
                "performer": getattr(msg.audio, "performer", "Unknown"),
            }
        elif msg.document:
            # fallback for generic documents
            doc_name = None
            if msg.document.attributes:
                for attr in msg.document.attributes:
                    if hasattr(attr, "file_name"):
                        doc_name = attr.file_name
                        break
            return {
                "file_id": msg.id,
                "title": doc_name or "Unknown_file",
                "performer": "Unknown",
            }

    return None





async def download_audio(message_id: int, path: str):
    """Download a specific audio or document message by message_id."""
    async for msg in client.iter_messages(EXTERNAL_BOT, ids=message_id):
        filename = "Unknown"

        if msg.audio:
            performer = getattr(msg.audio, "performer", "Unknown")
            title = getattr(msg.audio, "title", "Unknown")
            filename = f"{performer} - {title}.mp3"
            await msg.download_media(file=f"{path}/{filename}")
            return filename

        elif msg.document:
            # Try to get original file name if available
            doc_name = None
            if msg.document.attributes:
                for attr in msg.document.attributes:
                    if hasattr(attr, "file_name"):
                        doc_name = attr.file_name
                        break
            filename = doc_name or "Unknown_file"
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
