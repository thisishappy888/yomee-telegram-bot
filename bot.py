import os
import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher
from config_reader import config

from handlers import bot_messages, user_commands, question
from callbacks import callbacks


# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[
                        logging.FileHandler("bot.log", encoding='utf-8'),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)



def init_database():
    if not os.path.exists('data/database.db'):
        try:
            with sqlite3.connect('data/database.db') as db:
                cursor = db.cursor()

                cursor.execute("""
                    CREATE TABLE users(
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    age INTEGER,
                    gender TEXT,
                    geo TEXT,
                    about TEXT,
                    photo TEXT)
                """)
            
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS likes (
                        from_user_id INTEGER,
                        to_user_id INTEGER,
                        PRIMARY KEY (from_user_id, to_user_id)
                    )
                """)
                logger.info("База данных успешно инициализирована")
        except Exception as e:
            logger.error("Ошибка при инициализации базы данных", exc_info=True)



async def main():
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher()
    
    logger.info("Бот запущен")

    dp.include_routers(
        user_commands.router,
        bot_messages.router, 
        question.router,
        callbacks.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    


if __name__ == "__main__":
    init_database()
    asyncio.run(main())