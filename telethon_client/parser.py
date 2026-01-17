import asyncio
from telethon_client.client import client
from bot.config import EXTERNAL_BOT
from telethon import functions, types, events

async def query_external_bot_first(song_name: str):
    print(">>> Sending query:", song_name)
    await client.send_message(EXTERNAL_BOT, song_name)

    # 1️⃣ Find the menu message
    async for msg in client.iter_messages(EXTERNAL_BOT, limit=10):
        if not msg.reply_markup:
            continue
        print(">>> Menu found, msg_id =", msg.id)
        
        button = msg.reply_markup.rows[0].buttons[0]
        menu_msg_id = msg.id

        loop = asyncio.get_running_loop()
        future = loop.create_future()

        # 2️⃣ Listen for NEW media messages AFTER menu
        @client.on(events.NewMessage(chats=EXTERNAL_BOT))
        async def handler(event):
            m = event.message

            # Must be newer than the menu
            if m.id <= menu_msg_id:
                return

            # Must be actual media
            if not (m.audio or m.document):
                return

            if not future.done():
                future.set_result(m)

        try:
            print(">>> Clicking button at", datetime.utcnow().isoformat())
            # 3️⃣ Click the first button
            await client(
                functions.messages.GetBotCallbackAnswerRequest(
                    peer=EXTERNAL_BOT,
                    msg_id=menu_msg_id,
                    data=button.data
                )
            )
            print(">>> Button clicked")

            # 4️⃣ Wait for resulting file
            media_msg = await asyncio.wait_for(future, timeout=15)
            return {"file_id": media_msg.id}

        finally:
            client.remove_event_handler(handler)

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
