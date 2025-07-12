from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


# Главное меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Смотреть анкеты"),
            KeyboardButton(text="Заполнить анкету заново")
        ],
        [
            KeyboardButton(text="Изменить фото/видео"),
            KeyboardButton(text="Изменить текст анкеты"),
        ]
    ],
    resize_keyboard=True
)


# Выбор пола
gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="парень"),
            KeyboardButton(text="девушка"),
        ]
    ],
    resize_keyboard=True
)


# Кнопка с геолокацией
geo_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📍 Отправить геолокацию", request_location=True)]],
    resize_keyboard=True
)