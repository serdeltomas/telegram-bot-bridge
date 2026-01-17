# bot/handlers.py
from aiogram import Router, F
from aiogram.types import Message
from telethon_client.parser import query_external_bot_first, download_audio
from bot.config import DOWNLOAD_PATH

router = Router()

@router.message(F.text)
async def handle_search(message: Message):
    # get only the first audio/document from @fmusbot
    file_info = await query_external_bot_first(message.text, DOWNLOAD_PATH)

    if not file_info:
        await message.answer("❌ No audio found")
        return

    filename = await download_audio(file_info["file_id"], DOWNLOAD_PATH)

    if filename:
        await message.answer(f"✅ Downloaded: {filename}")
    else:
        await message.answer("❌ Download failed")
