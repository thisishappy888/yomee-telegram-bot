from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()
    geo = State()
    about = State()
    photo = State()