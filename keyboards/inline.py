from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_rating_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍", callback_data=f"like:{user_id}"),
                InlineKeyboardButton(text="📝", callback_data=f"message:{user_id}"),
                InlineKeyboardButton(text="👎", callback_data="dislike"),
            ],
            [
                InlineKeyboardButton(text="Пожаловаться", callback_data="report"),
                InlineKeyboardButton(text="Анонимное сообщение", callback_data=f"anonymous_message:{user_id}"),
            ]
        ]
    )
