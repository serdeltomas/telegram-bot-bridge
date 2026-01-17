import asyncio
from telethon_client.client import client
from bot.config import EXTERNAL_BOT
from telethon import functions, events

async def query_external_bot_first(song_name: str):
    print(">>> Sending query:", song_name)
    await client.send_message(EXTERNAL_BOT, song_name)

    # 1️⃣ Get the latest menu message with buttons
    menu_msg = None
    async for msg in client.iter_messages(EXTERNAL_BOT, limit=10):
        if msg.reply_markup:
            menu_msg = msg
            break  # take the newest one (iter_messages returns newest first)

    if not menu_msg:
        print(">>> No menu found")
        return None

    print(">>> Latest menu found, msg_id =", menu_msg.id, "at", menu_msg.date.isoformat())

    # 2️⃣ Pick the first button
    first_button = menu_msg.reply_markup.rows[0].buttons[0]

    # 3️⃣ Prepare a future to wait for the media
    loop = asyncio.get_running_loop()
    future = loop.create_future()

    # 4️⃣ Handler to catch the next audio/document sent by the bot
    @client.on(events.NewMessage(chats=EXTERNAL_BOT))
    async def handler(event):
        m = event.message
        if m.audio or m.document:
            print(">>> Accepted media msg:", m.id, m.date.isoformat())
            if not future.done():
                future.set_result(m)

    try:
        # 5️⃣ Click the button
        print(">>> Clicking button")
        await client(
            functions.messages.GetBotCallbackAnswerRequest(
                peer=EXTERNAL_BOT,
                msg_id=menu_msg.id,
                data=first_button.data
            )
        )

        # 6️⃣ Wait for the media to arrive (timeout 20s)
        media_msg = await asyncio.wait_for(future, timeout=20)
        return {"file_id": media_msg.id}

    except asyncio.TimeoutError:
        print(">>> Timeout: No media received from bot")
        return None

    finally:
        # Always remove handler to avoid memory leaks
        client.remove_event_handler(handler)


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
