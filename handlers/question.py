import logging
import sqlite3
import aiohttp

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from utils.states import Form
from keyboards import reply


router = Router()
logger = logging.getLogger(__name__)



@router.message(Form.name)
async def form_name(message: Message, state: FSMContext):
    """Обработка ввода имени"""
    await state.update_data(name = message.text)
    await state.set_state(Form.age)
    await message.answer('Введите ваш возраст')



@router.message(Form.age)
async def form_age(message: Message, state: FSMContext):
    """Обработка ввода возраста"""
    if message.text.isdigit():
        await state.update_data(age = message.text)
        await state.set_state(Form.gender)
        await message.answer('Укажите ваш пол (парень/девушка)', reply_markup=reply.gender_kb)
    else:
        await message.answer('Пожалуйста, введите число!')



@router.message(Form.gender, F.text.casefold().in_(['парень', 'девушка']))
async def form_gender(message: Message, state: FSMContext):
    """Обработка выбора пола"""
    await state.update_data(gender = message.text)
    await state.set_state(Form.geo)
    await message.answer(
        "Отправьте вашу геолокацию, чтобы определить город", 
        reply_markup=reply.geo_kb
    )



@router.message(Form.gender)
async def incorrect_form_gender(message: Message, state: FSMContext):
    """Обработка некорректного ввода пола"""
    await message.answer('Пожалуйста, выберите вариант из предложенных!')



@router.message(Form.geo, F.location)
async def form_geo(message: Message, state: FSMContext):
    """Определение города по геолокации"""
    lat, lon = message.location.latitude, message.location.longitude
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"


    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={"User-Agent": "geo-bot/1.0"}) as response:
                if response.status == 200:
                    data = await response.json()
                    city = (
                        data.get("address", {}).get("city") or
                        data.get("address", {}).get("town") or
                        data.get("address", {}).get("village") or
                        "неизвестное место"
                    )
                else:
                    await message.answer("Не удалось определить город. Попробуйте ещё раз!")
    except Exception as e:
        logger.error("Ошибка при запросе геолокации", exc_info=True)


    await state.update_data(geo = city)
    await state.set_state(Form.about)
    await message.answer('Теперь расскажите о себе')



@router.message(Form.about)
async def form_about(message: Message, state: FSMContext):
    """Обработка информации 'о себе'"""
    await state.update_data(about = message.text)
    await state.set_state(Form.photo)
    await message.answer('Отправьте ваше фото')



@router.message(Form.photo)
async def form_photo(message: Message, state: FSMContext):
    """Финал: сохраняем акнету и показываем пользователю"""
    try:
        photo_file_id = message.photo[-1].file_id
    except (IndexError, AttributeError):
        await message.answer("❌ Пожалуйста, отправьте фотографию.")
    

    data = await state.get_data()
    await state.clear()


    try:
        with sqlite3.connect("data/database.db") as db:
            cursor = db.cursor()
            cursor.execute("""
                INSERT INTO users(id, name, age, gender, geo, about, photo) 
                VALUES(?, ?, ?, ?, ?, ?, ?)
            """, (
                message.from_user.id,
                data['name'], 
                data['age'], 
                data['gender'],
                data['geo'], 
                data['about'], 
                photo_file_id
            ))


            logger.info(
                f"Новая анкета: ID={message.from_user.id}, Name={data['name']}, Age={data['age']}, "
                f"Gender={data['gender']}, Geo={data['geo']}, About={data['about']}"
            )


    except Exception as e:
        logger.error("Ошибка при сохранении в базу данных", exc_info=True)

    await message.answer_photo(
        photo=photo_file_id, 
        caption=f"{data['name']}, {data['age']}, {data['geo']} - {data['about']}", 
        reply_markup=reply.main_kb
    )
