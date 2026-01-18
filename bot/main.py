import asyncio
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers import router
from telethon_client.client import start_client
from telethon_client.batch import process_csv

async def main():
    # Start Telethon client ONCE
    await start_client()

    # 🔥 RUN CSV IMPORT HERE
    await process_csv("songs.csv")

    # Start Telegram bot AFTER batch finishes
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
