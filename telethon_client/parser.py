import asyncio
from telethon_client.client import client
from bot.config import EXTERNAL_BOT
from telethon import functions, types

async def query_external_bot_first(song_name: str):
    """Send song query and download the first FMUS file automatically."""
    await client.send_message(EXTERNAL_BOT, song_name)

    
    # Wait a short moment for the bot to respond
    await asyncio.sleep(2)  # tweak if needed

    async for msg in client.iter_messages(EXTERNAL_BOT, limit=1):
        if msg.reply_markup:  # There are inline buttons

            first_button = msg.reply_markup.rows[0].buttons[0]
            button_data = first_button.data

            # Trigger the button to get the audio/document
            response = await client(
                functions.messages.GetBotCallbackAnswerRequest(
                    peer=EXTERNAL_BOT,
                    msg_id=msg.id,
                    data=button_data
                )
            )

            # Wait for the bot to send the actual file
            await asyncio.sleep(1)

            # Now fetch the resulting message that contains the actual file
            async for file_msg in client.iter_messages(EXTERNAL_BOT, limit=1):
                if file_msg.audio or file_msg.document:
                    # return first found file
                    return {"file_id": file_msg.id}
                    
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
