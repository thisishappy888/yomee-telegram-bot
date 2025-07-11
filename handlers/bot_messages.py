import logging
import sqlite3

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import inline
from utils.model import get_best_match
from utils.states import Form, ChangeForm


router = Router()
logger = logging.getLogger(__name__)



@router.message(F.text.lower() == "смотреть анкеты")
async def look_question(message: Message, state: FSMContext):
    """Показывает подходящие анкеты пользователю"""
    user_id = message.from_user.id

    try:
        best_match_id = get_best_match(user_id)

        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()

            cursor.execute("SELECT age FROM users WHERE id = ?", (message.from_user.id,))
            age_row = cursor.fetchone()

            user_age = int(age_row[0])
            

            if best_match_id:
                cursor.execute("""
                    SELECT * FROM users 
                    WHERE id = ? AND age IN (?, ?, ?)
                """, (best_match_id, user_age, user_age - 1, user_age + 1))
            else:
                cursor.execute("""
                    SELECT * FROM users 
                    WHERE id != ? AND age IN (?, ?, ?) 
                    ORDER BY RANDOM() LIMIT 1
                """, (user_id, user_age, user_age - 1, user_age + 1))
           
        
            question = cursor.fetchone()


            if question:
                await message.answer_photo(
                    photo=question[6], 
                    caption=f"{question[1]}, {question[2]}, {question[4]} - {question[5]}", 
                    reply_markup=inline.get_rating_kb(question[0])
                )
            else:
                await message.answer("😔 Пока нет подходящих анкет. Попробуйте позже!")
            

    except Exception as e:
        logging.error("Не удалось выполнить запрос к базе данных", exc_info=True)



@router.message(F.text.lower() == "заполнить анкету заново")
async def change_profile(message: Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer("Введите имя")


@router.message(F.text.lower() == "изменить фото/видео")
async def change_profile(message: Message, state: FSMContext):
    await state.set_state(ChangeForm.photo)
    await message.answer("Отправьте фото")


@router.message(F.text.lower() == "изменить текст анкеты")
async def change_profile(message: Message, state: FSMContext):
    await state.set_state(ChangeForm.bio)
    await message.answer("Расскажи о себе")