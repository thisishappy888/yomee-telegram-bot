from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Смотреть анкеты"),
            KeyboardButton(text="Моя анкета")
        ]
    ],
    resize_keyboard=True
)

change_form_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="⚙️"),
            KeyboardButton(text="😎"),
            KeyboardButton(text="📷"),
        ]
    ],
    resize_keyboard=True
)

gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="парень"),
            KeyboardButton(text="девушка"),
        ]
    ],
    resize_keyboard=True
)

geo_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]],
    resize_keyboard=True
)