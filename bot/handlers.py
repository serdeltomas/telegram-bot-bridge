from aiogram import types, Router
from parser import query_external_bot, download_audio_from_selection
from bot.config import DOWNLOAD_PATH

router = Router()
user_cache = {}  # store user choices

@router.message(commands=["search"])
async def handle_search(message: types.Message):
    query = message.get_args()
    if not query:
        await message.answer("Please provide a song name, e.g., /search Imagine Dragons")
        return

    options = await query_external_bot(query)
    if not options:
        await message.answer("❌ No audio found")
        return

    # Show options to user
    text = "Select a song to download:\n\n"
    for i, opt in enumerate(options, start=1):
        text += f"{i}. {opt['title']}\n"
    await message.answer(text)

    # Cache options for user
    user_cache[message.from_user.id] = options

@router.message()
async def handle_selection(message: types.Message):
    # Check if user has cached options
    if message.from_user.id not in user_cache:
        return

    try:
        idx = int(message.text) - 1
    except ValueError:
        await message.answer("Please send a valid number from the list")
        return

    options = user_cache[message.from_user.id]
    if not 0 <= idx < len(options):
        await message.answer("Invalid selection")
        return

    opt = options[idx]
    await message.answer("⏳ Downloading...")

    # Click button + download
    path = await download_audio_from_selection(opt["msg_id"], opt["data"], DOWNLOAD_PATH)
    if path:
        await message.answer(f"✅ Downloaded: {path}")
    else:
        await message.answer("❌ Failed to download audio")

    # Clear cache
    del user_cache[message.from_user.id]
