import asyncio
from telethon_client.client import client
from bot.config import EXTERNAL_BOT


async def query_external_bot(song_name: str):
"""Send song query to @fmusbot and collect audio options."""
await client.send_message(EXTERNAL_BOT, song_name)


options = []
async for msg in client.iter_messages(EXTERNAL_BOT, limit=10):
if msg.audio:
options.append({
"file_id": msg.id,
"title": msg.audio.title or "Unknown",
"performer": msg.audio.performer or "Unknown",
"duration": msg.audio.duration
})
if len(options) >= 5:
break


return options


async def download_audio(message_id: int, path: str):
async for msg in client.iter_messages(EXTERNAL_BOT, ids=message_id):
if msg.audio:
filename = f"{msg.audio.performer} - {msg.audio.title}.mp3"
await msg.download_media(file=f"{path}/{filename}")
return filename
return None
```python
from telethon_client.client import client
from bot.config import EXTERNAL_BOT


async def query_external_bot(query: str):
await client.send_message(EXTERNAL_BOT, query)


responses = []
async for msg in client.iter_messages(EXTERNAL_BOT, limit=5):
if msg.text:
responses.append(msg.text)
return responses


async def download_latest_file(filename: str, path: str):
async for msg in client.iter_messages(EXTERNAL_BOT, limit=1):
if msg.file:
await msg.download_media(file=f"{path}/{filename}")
return True
return False
