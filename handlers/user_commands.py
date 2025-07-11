import logging
import sqlite3

from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.states import Form
from keyboards import inline, reply


router = Router()
logger = logging.getLogger(__name__)



@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """Обработка команды /start"""
    user_id = message.from_user.id
    logger.info(f"Пользователь {user_id} использует команду /start")


    try:
        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()
            cursor.execute('SELECT * FROM users WHERE id=(?)', (message.from_user.id,))
            user_data = cursor.fetchone()

    except Exception as e:
        logger.error("Не удалось выполнить запрос к базе данных", exc_info=True)


    if user_data:
        await message.answer("Вот так выглядит твоя анкета:")
        try:
            await message.answer_photo(
                photo=user_data[6], 
                caption=f"{user_data[1]}, {user_data[2]}, {user_data[4]} - {user_data[5]}", 
                reply_markup=reply.main_kb)
        except Exception as e:
            logger.warning("Ошибка при отправке фото профиля", exc_info=True)
    else:
        await state.set_state(Form.name)
        await message.answer_sticker(
            sticker="CAACAgIAAxkBAAEQk6RocTuu4bjUEmWRLwn0NtFE4zbqnAACwjYAArGLYUgUKsMUgjbO6DYE"
        )
        await message.answer('Давай создадим анкету.\nВведи свое имя')
