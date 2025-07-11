import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.states import Form

from keyboards import inline, reply

import sqlite3

router = Router()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    """Обработка команды /start"""
    logging.info(f"Пользователь {message.from_user.id} использует команду /start")
    try:
        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()

            cursor.execute('SELECT * FROM users WHERE id=(?)', (message.from_user.id,))

            result = cursor.fetchone()
    except Exception as e:
        logging.error("Не удалось выполнить запрос к базе данных", exc_info=True)

    if result:
        try:
            with sqlite3.connect("data/database.db") as db:
                cursor = db.cursor()

                cursor.execute('SELECT * FROM users WHERE id=(?)', (message.from_user.id,))

        except Exception as e:
            logging.error("Не удалось выполнить запрос к базе данных", exc_info=True)

        question = cursor.fetchone()
        await message.answer("Вот так выглядит твоя анкета:")
        print(question)
        await message.answer_photo(photo=question[6], caption=f"{question[1]}, {question[2]}, {question[4]} - {question[5]}", reply_markup=reply.main_kb)
    else:
        await state.set_state(Form.name)
        await message.answer('👋 Привет! Давай создадим анкету.\nВведи свое имя')
