import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config_reader import config


bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Привет! Я бот на aiogram 3.x и poetry 😊")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
