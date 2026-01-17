import asyncio
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers import router
from telethon_client.client import start_client


async def main():
await start_client()


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)


await dp.start_polling(bot)


if __name__ == '__main__':
asyncio.run(main())
