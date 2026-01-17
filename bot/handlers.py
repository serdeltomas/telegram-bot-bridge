from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from telethon_client.parser import query_external_bot, download_audio_from_selection
from bot.config import DOWNLOAD_PATH

router = Router()
user_cache = {}

@router.message(F.text)
async def handle_search(message: Message):
    # query @fmusbot for audio options
    options = await query_external_bot(message.text)

    if not options:
        await message.answer("❌ No audio found")
        return

    keyboard = []
    for idx, opt in enumerate(options):
        user_cache[f"{message.from_user.id}:{idx}"] = opt["file_id"]
        keyboard.append([
            InlineKeyboardButton(
                text=f"🎵 {opt['performer']} - {opt['title']}",
                callback_data=str(idx)
            )
        ])

    await message.answer(
        "🎧 Select audio:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@router.callback_query()
async def handle_download(call: CallbackQuery):
    await call.answer()

    key = f"{call.from_user.id}:{call.data}"
    msg_id = user_cache.get(key)

    if not msg_id:
        await call.message.edit_text("❌ Session expired")
        return

    filename = await download_audio_from_selection(msg_id, DOWNLOAD_PATH)

    if filename:
        await call.message.edit_text(f"✅ Downloaded: {filename}")
    else:
        await call.message.edit_text("❌ Download failed")
