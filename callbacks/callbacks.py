from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from keyboards import inline
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from utils.states import UserStates

import logging

import sqlite3

router = Router()

logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'dislike')
async def dislike(callback: CallbackQuery, bot: Bot):
    message_id_to_delete = callback.message.message_id
    await bot.delete_message(chat_id=callback.message.chat.id, message_id=message_id_to_delete)
    
    try:
        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()

            cursor.execute('SELECT * FROM users WHERE id != ? ORDER BY RANDOM() LIMIT 1', (callback.message.from_user.id,))
        
            question = cursor.fetchone()

            await callback.message.answer_photo(photo=question[6], caption=f"{question[1]}, {question[2]}, {question[4]} - {question[5]}", reply_markup=inline.get_rating_kb(question[0]))

    except Exception as e:
        logger.error("Не удалось выполнить запрос к базе данных", exc_info=True)



@router.callback_query(F.data.startswith('anonymous_message:'))
async def message_waiting(callback: CallbackQuery, bot: Bot, state: FSMContext):
    # Сохраняем ID получателя в состоянии
    to_user_id = int(callback.data.split(":")[1])
    await state.update_data(to_user_id=to_user_id)
    
    await callback.message.answer("Пожалуйста, отправьте ваше сообщение:")
    await state.set_state(UserStates.waiting_for_message)


@router.message(UserStates.waiting_for_message)
async def user_message(message: Message, state: FSMContext, bot: Bot):
    try:
        # Получаем сохраненные данные из состояния
        data = await state.get_data()
        to_user_id = data['to_user_id']
        from_user_id = message.from_user.id
        
        # Подключаемся к базе данных
        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()

            # Получаем данные отправителя
            cursor.execute("SELECT * FROM users WHERE id = ?", (from_user_id,))
            from_user_data = cursor.fetchone()
            
            if not from_user_data:
                await message.answer("❌ Ваш профиль не найден")
                return

            # Отправляем сообщение получателю
            await bot.send_message(
                chat_id=to_user_id,
                text=f"🔒 Анонимное сообщение:\n{message.text}"
            )

            await message.answer("✅ Сообщение отправлено анонимно!")

    except Exception as e:
        print(f"Ошибка: {e}")
        await message.answer("❌ Не удалось отправить сообщение")
    
    finally:
        await state.clear()



@router.callback_query(F.data.startswith('like:'))
async def like(callback: CallbackQuery, bot: Bot):
    try:
        # Получаем ID пользователей
        from_user_id = callback.from_user.id
        to_user_id = int(callback.data.split(":")[1])
        
        # Подключаемся к базе данных
        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()

            # 1. Получаем данные отправителя
            cursor.execute("SELECT * FROM users WHERE id = ?", (from_user_id,))
            from_user_data = cursor.fetchone()
            
            if not from_user_data:
                await callback.answer("❌ Ваш профиль не найден", show_alert=True)
                return

            # 2. Отправляем профиль получателю
            await bot.send_photo(
                chat_id=to_user_id,
                photo=from_user_data[6],
                caption=f"{from_user_data[1]}, {from_user_data[2]}, {from_user_data[4]} - {from_user_data[5]}",
                reply_markup=inline.get_rating_kb(from_user_data[0])
            )

            # 3. Проверяем взаимный лайк
            cursor.execute("""
                SELECT 1 FROM likes 
                WHERE from_user_id = ? AND to_user_id = ?
            """, (to_user_id, from_user_id))
            
            mutual_like_exists = cursor.fetchone()

            # 4. Записываем текущий лайк в базу
            cursor.execute("""
                INSERT OR IGNORE INTO likes (from_user_id, to_user_id)
                VALUES (?, ?)
            """, (from_user_id, to_user_id))
            db.commit()

            # 5. Если есть взаимный лайк - уведомляем обоих
            if mutual_like_exists:
                # Получаем данные получателя
                cursor.execute("SELECT * FROM users WHERE id = ?", (to_user_id,))
                to_user_data = cursor.fetchone()
                
                if to_user_data:
                    # Сообщение отправителю о взаимной симпатии
                    await bot.send_message(
                        from_user_id,
                        f"💞 Взаимная симпатия! Вы понравились {to_user_data[0]}!\n"
                        f"Написать: [перейти в личку](tg://user?id={to_user_id})", parse_mode="Markdown"
                    )
                    
                    # Сообщение получателю о взаимной симпатии
                    await bot.send_message(
                        to_user_id,
                        f"💞 Взаимная симпатия! Вы понравились {from_user_data[1]}!\n"
                        f"Написать: [перейти в личку](tg://user?id={from_user_id})", parse_mode="Markdown"
                    )

        await callback.answer("✅ Лайк отправлен!", show_alert=False)

    except ValueError:
        await callback.answer("❌ Ошибка: неверный ID пользователя", show_alert=True)
    except Exception as e:
        print(f"Ошибка: {e}")
        await callback.answer("❌ Не удалось отправить лайк", show_alert=True)