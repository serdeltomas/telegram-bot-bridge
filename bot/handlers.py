# bot/handlers.py
from aiogram import Router, F
from aiogram.types import Message
from telethon_client.parser import query_external_bot_first
from bot.config import DOWNLOAD_PATH

router = Router()

@router.message(F.text)
async def handle_search(message: Message):
    # query bot, click latest menu, download audio
    filename = await query_external_bot_first(message.text, DOWNLOAD_PATH)

    if filename:
        await message.answer(f"✅ Downloaded: {filename}")
    else:
        await message.answer("❌ No audio found")
