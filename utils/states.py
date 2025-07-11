from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()
    geo = State()
    about = State()
    photo = State()

class UserStates(StatesGroup):
    waiting_for_anonymous_message = State()  # Состояние ожидания сообщения
    waiting_for_message = State()
