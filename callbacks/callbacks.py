import logging
import sqlite3

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import inline
from utils.states import UserStates


router = Router()
logger = logging.getLogger(__name__)



def get_user_from_db(user_id: int):
    """получает пользователя из базы данных"""
    with sqlite3.connect("data/database.db") as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        return cursor.fetchone()
    


def check_mutual_like(cursor, from_user_id: int, to_user_id: int):
    """проверяет лайкнули ли анкету взаимно"""
    cursor.execute(
        "SELECT 1 FROM likes WHERE from_user_id = ? AND to_user_id = ?", 
        (to_user_id, from_user_id))
    return cursor.fetchone()



def save_like(cursor, from_user_id: int, to_user_id: int):
    """сохраняет лайки"""
    cursor.execute(
        "INSERT OR IGNORE INTO likes (from_user_id, to_user_id) VALUES (?, ?)", 
        (from_user_id, to_user_id)
    )



async def send_user_profile(bot: Bot, chat_id: int, user_data: tuple):
    """отправляет анкету пользователя"""
    await bot.send_photo(
        chat_id=chat_id,
        photo=user_data[6],
        caption=f"{user_data[1]}, {user_data[2]}, {user_data[4]} - {user_data[5]}",
        reply_markup=inline.get_rating_kb(user_data[0])
    )



@router.callback_query(F.data == 'dislike')
async def dislike(callback: CallbackQuery, bot: Bot):
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    
    try:
        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()

            cursor.execute(
                'SELECT * FROM users WHERE id != ? ORDER BY RANDOM() LIMIT 1', 
                (callback.message.from_user.id,))
        
            question = cursor.fetchone()

            await callback.message.answer_photo(
                photo=question[6], 
                caption=f"{question[1]}, {question[2]}, {question[4]} - {question[5]}", 
                reply_markup=inline.get_rating_kb(question[0])
            )

    except Exception as e:
        logger.error("Не удалось выполнить запрос к базе данных", exc_info=True)



@router.callback_query(F.data.startswith('anonymous_message:'))
async def anonymous_message_waiting(callback: CallbackQuery, bot: Bot, state: FSMContext):
    to_user_id = int(callback.data.split(":")[1])
    await state.update_data(to_user_id=to_user_id)
    await callback.message.answer("Пожалуйста, отправьте ваше сообщение:")
    await state.set_state(UserStates.waiting_for_anonymous_message)



@router.message(UserStates.waiting_for_anonymous_message)
async def user_anonymous_message(message: Message, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        to_user_id = data['to_user_id']
        from_user_id = message.from_user.id
        
        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()

            cursor.execute("SELECT * FROM users WHERE id = ?", (from_user_id,))
            from_user_data = cursor.fetchone()
            
            if not from_user_data:
                await message.answer("❌ Ваш профиль не найден")
                return

            await bot.send_message(to_user_id, f"🔒 Анонимное сообщение:\n{message.text}")
            await message.answer("✅ Сообщение отправлено анонимно!")

    except Exception as e:
        logger.exception("Ошибка при отправке анонимного сообщения")
        await message.answer("❌ Не удалось отправить сообщение")
    finally:
        await state.clear()



@router.callback_query(F.data.startswith('message:'))
async def message_waiting(callback: CallbackQuery, bot: Bot, state: FSMContext):
    to_user_id = int(callback.data.split(":")[1])
    await state.update_data(to_user_id=to_user_id)
    await callback.message.answer("Пожалуйста, отправьте ваше сообщение:")
    await state.set_state(UserStates.waiting_for_message)



@router.message(UserStates.waiting_for_message)
async def user_message(message: Message, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        to_user_id = data['to_user_id']
        from_user_id = message.from_user.id

        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()

            from_user_data = get_user_from_db(from_user_id)

            await message.answer("Вы понравились:")
            await send_user_profile(bot, to_user_id, from_user_data)
            await bot.send_message(to_user_id, f"сообщение:\n{message.text}")

            mutual = check_mutual_like(cursor, from_user_id, to_user_id)
            save_like(cursor, from_user_id, to_user_id)
            db.commit()

            if mutual:
                to_user_data = get_user_from_db(to_user_id)     
                if to_user_data:
                    await bot.send_message(
                        from_user_id,
                        f"💞 Взаимная симпатия! Вы понравились {to_user_data[1]}!\n"
                        f"Написать: [перейти в личку](tg://user?id={to_user_data[0]})", parse_mode="Markdown"
                    )
                    await bot.send_message(
                        to_user_id,
                        f"💞 Взаимная симпатия! Вы понравились {from_user_data[1]}!\n"
                        f"Написать: [перейти в личку](tg://user?id={from_user_data[0]})", parse_mode="Markdown"
                    )

    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await state.clear()



@router.callback_query(F.data.startswith('like:'))
async def like(callback: CallbackQuery, bot: Bot):
    try:
        from_user_id = callback.from_user.id
        to_user_id = int(callback.data.split(":")[1])
        
        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()

            from_user_data = get_user_from_db(from_user_id)

            mutual = check_mutual_like(cursor, from_user_id, to_user_id)
            save_like(cursor, from_user_id, to_user_id)
            db.commit()

            if mutual:
                to_user_data = get_user_from_db(to_user_id)
                if to_user_data:
                    await bot.send_message(
                        from_user_id,
                        f"💞 Взаимная симпатия! Вы понравились {to_user_data[0]}!\n"
                        f"Написать: [перейти в личку](tg://user?id={to_user_id})", parse_mode="Markdown"
                    )
                    await bot.send_message(
                        to_user_id,
                        f"💞 Взаимная симпатия! Вы понравились {from_user_data[1]}!\n"
                        f"Написать: [перейти в личку](tg://user?id={from_user_id})", parse_mode="Markdown"
                    )

        await callback.answer("✅ Лайк отправлен!", show_alert=False)

    except Exception as e:
        logger.error(f"Ошибка: {e}")