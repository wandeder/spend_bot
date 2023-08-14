import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from spend_bot.sheets import save_to_sheet


# Загрузка переменных окружения из .env
load_dotenv()

# Объявление и инициализация объектов бота и диспетчера
bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

# Настройка логирования в stdout
logging.basicConfig(level=logging.INFO)

# Список категорий трат и доступных валют
categories_names = ['Еда', 'Транспорт', 'Крупные покупки',
                    'Жилье', 'Другое', 'Учеба', 'Связь', 'Доходы', 'Обмен']
currency_names = ["Лари", "Рубли", 'Доллары', 'Евро', 'Лиры']


class RegisterSpend(StatesGroup):
    waiting_money = State()
    waiting_currency = State()
    waiting_category = State()
    waiting_comment = State()
    waiting_record = State()


@dp.message_handler(commands='start', state='*')
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
            'Запиши свои траты:',
            reply_markup=types.ReplyKeyboardRemove(),
            )


@dp.message_handler()
async def start_bot(message: types.Message, state: FSMContext):
    await state.finish()
    try:
        spend = float(message.text.replace(',', '.'))
    except ValueError:
        await message.answer('Введи нормальное число!')
        return
    else:
        await state.update_data(value=spend)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for name in currency_names:
            keyboard.add(name)
        await RegisterSpend.waiting_currency.set()
        await message.answer("Выбери валюту:", reply_markup=keyboard)


@dp.message_handler(state=RegisterSpend.waiting_currency)
async def chose_currency(message: types.Message, state: FSMContext):
    if message.text not in currency_names:
        await message.answer('Выбери валюту!')
        return
    await state.update_data(currency=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories_names:
        keyboard.add(category)
    await RegisterSpend.waiting_category.set()
    await message.answer(
            'Теперь выбери категорию трат:',
            reply_markup=keyboard,
            )


@dp.message_handler(state=RegisterSpend.waiting_category)
async def chose_category(message: types.Message, state: FSMContext):
    if message.text not in categories_names:
        await message.answer('Выбери категорию!')
        return
    await state.update_data(category=message.text)
    await RegisterSpend.waiting_comment.set()
    await message.answer(
            'Введи комментарий:',
            reply_markup=types.ReplyKeyboardRemove(),
            )


@dp.message_handler(state=RegisterSpend.waiting_comment)
async def comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)
    # Данные о трате для записи в таблицу
    user_data = await state.get_data()
    # Запись в Google таблицу
    save_to_sheet(user_data)
    await message.bot.send_message(os.getenv('CHAT_ID'),
                                   text=get_text(user_data)
                                   )
    await state.finish()


# Сгенерировать сообщение о тратах в чат
def get_text(data):
    value = data['value']
    currency = data['currency'].lower()
    category = data['category'].lower()
    if data['comment'] == 'Нет комментария':
        comment = ''
    else:
        comment = f"{data['comment']}."
    return f"{value} {currency} потрачено на {category}. {comment}"


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
