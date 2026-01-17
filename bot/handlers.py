from aiogram import types
from aiogram.dispatcher.filters import Command
from telethon_client.parser import query_external_bot, download_audio
from bot.main import router


@router.message(Command("search"))
async def handle_search(message: types.Message):
    # Get song name
    song_name = message.text.split(maxsplit=1)[1] if " " in message.text else message.text

    await message.answer(f"🔎 Searching for: {song_name}")

    audio_msg = await query_external_bot(song_name)
    if not audio_msg:
        await message.answer("❌ No audio found")
        return

    filename = await download_audio(audio_msg)
    await message.answer(f"✅ Downloaded: {filename}")
