from telethon import functions
from telethon_client.client import client
from bot.config import EXTERNAL_BOT, DOWNLOAD_PATH


async def query_external_bot(song_name: str):
    """Send song query to fmusbot and return the first track."""
    await client.send_message(EXTERNAL_BOT, song_name)

    # Wait and get recent messages
    async for msg in client.iter_messages(EXTERNAL_BOT, limit=5):
        # Check if message contains buttons (track list)
        if msg.reply_markup:
            # Take the first button
            first_button = msg.reply_markup.rows[0].buttons[0]
            
            # Click the button
            await client(functions.messages.GetBotCallbackAnswerRequest(
                peer=EXTERNAL_BOT,
                msg_id=msg.id,
                data=first_button.data
            ))

            # After clicking, get the audio
            async for audio_msg in client.iter_messages(EXTERNAL_BOT, limit=5):
                if audio_msg.audio or audio_msg.document:
                    return audio_msg  # Return first audio found

    return None


async def download_audio(audio_msg):
    """Download a Telethon audio/document message."""
    if audio_msg.audio:
        title = audio_msg.audio.title or "Unknown"
        performer = audio_msg.audio.performer or "Unknown"
        filename = f"{performer} - {title}.mp3"
    else:
        # fallback for documents
        filename = f"{audio_msg.id}.mp3"

    path = f"{DOWNLOAD_PATH}/{filename}"
    await audio_msg.download_media(file=path)
    return filename
