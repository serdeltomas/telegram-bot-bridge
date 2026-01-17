import asyncio
from telethon_client.client import client
from bot.config import EXTERNAL_BOT
from telethon import functions, types, events


async def query_external_bot_first(song_name: str):
    await client.send_message(EXTERNAL_BOT, song_name)

    # 1️⃣ Find the menu message
    async for msg in client.iter_messages(EXTERNAL_BOT, limit=10):
        if msg.reply_markup:
            first_button = msg.reply_markup.rows[0].buttons[0]

            # 2️⃣ Prepare waiter BEFORE clicking
            waiter = client.wait_for(
                events.NewMessage(
                    from_users=EXTERNAL_BOT
                ),
                timeout=15
            )

            # 3️⃣ Click first button
            await client(
                functions.messages.GetBotCallbackAnswerRequest(
                    peer=EXTERNAL_BOT,
                    msg_id=msg.id,
                    data=first_button.data
                )
            )

            # 4️⃣ Wait for the resulting file
            new_msg = await waiter

            if new_msg.audio or new_msg.document:
                return {"file_id": new_msg.id}

            return None

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
