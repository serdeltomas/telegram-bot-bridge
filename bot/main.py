import asyncio
from aiogram import Bot
from bot.handlers import router  # import router once
from bot.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

async def main():
    from aiogram import Dispatcher
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)  # if webhook not used
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
