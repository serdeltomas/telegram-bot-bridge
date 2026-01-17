import asyncio
from telethon_client.client import client
from bot.config import EXTERNAL_BOT
from telethon import functions, events
from telethon.tl.types import DocumentAttributeAudio

async def query_external_bot_first(song_name: str):
    print(">>> Sending query:", song_name)
    await client.send_message(EXTERNAL_BOT, song_name)

    loop = asyncio.get_running_loop()
    future_menu = loop.create_future()
    future_media = loop.create_future()

    # 1️⃣ Catch the new menu sent by the bot
    @client.on(events.NewMessage(chats=EXTERNAL_BOT))
    async def menu_handler(event):
        m = event.message
        if m.reply_markup:  # It's a menu
            print(">>> New menu received:", m.id, m.date.isoformat())
            if not future_menu.done():
                future_menu.set_result(m)

    try:
        # 2️⃣ Wait for the new menu to arrive (timeout 10s)
        menu_msg = await asyncio.wait_for(future_menu, timeout=10)
        first_button = menu_msg.reply_markup.rows[0].buttons[0]

        # 3️⃣ Catch the next media sent by the bot
        @client.on(events.NewMessage(chats=EXTERNAL_BOT))
        async def media_handler(event):
            m = event.message
            if m.audio or m.document:
                print(">>> Accepted media msg:", m.id, m.date.isoformat())
                if not future_media.done():
                    future_media.set_result(m)

        # 4️⃣ Click the button
        print(">>> Clicking button", first_button.text)
        await client(
            functions.messages.GetBotCallbackAnswerRequest(
                peer=EXTERNAL_BOT,
                msg_id=menu_msg.id,
                data=first_button.data
            )
        )

        # 5️⃣ Wait for the media to arrive (timeout 20s)
        media_msg = await asyncio.wait_for(future_media, timeout=20)
        return {"file_id": media_msg.id}

    except asyncio.TimeoutError:
        print(">>> Timeout: Bot did not send menu or media")
        return None

    finally:
        client.remove_event_handler(menu_handler)
        client.remove_event_handler(media_handler)


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
            # Check if the document has audio attributes
            performer = None
            title = None
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
            else:
                # fallback to original file name
                if hasattr(msg.document, "file_name") and msg.document.file_name:
                    filename = msg.document.file_name

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
