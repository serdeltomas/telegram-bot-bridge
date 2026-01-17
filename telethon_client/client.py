
from telethon import TelegramClient
from bot.config import API_ID, API_HASH


client = TelegramClient("user_session", API_ID, API_HASH)


async def start_client():
  if not client.is_connected():
    await client.start()
