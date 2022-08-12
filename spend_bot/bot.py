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

# Names categories of spending and names currency
categories_names = ['Еда', 'Транспорт', 'Крупные покупки',
                    'Жилье', 'Другое', 'Доходы']
currency_names = ['Лиры', 'Рубли', 'Доллары', 'Евро']


class RegisterSpend(StatesGroup):
    waiting_money = State()
    waiting_currency = State()
    waiting_category = State()


@dp.message_handler(commands='start', state='*')
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
            'Запиши свои траты:',
            reply_markup=types.ReplyKeyboardRemove()
            )


@dp.message_handler()
async def start_bot(message: types.Message, state: FSMContext):
    await state.finish()
    if not message.text.isdigit():
        await message.answer('Введи нормальное число!')
        return
    await state.update_data(value=int(message.text))
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
    await message.answer('Теперь выбери категорию трат:',
                         reply_markup=keyboard)


@dp.message_handler(state=RegisterSpend.waiting_category)
async def chose_category(message: types.Message, state: FSMContext):
    if message.text not in categories_names:
        await message.answer('Выбери категорию!')
        return
    await state.update_data(category=message.text)
    # Данные о трате для записи в таблицу
    user_data = await state.get_data()
    # Запись в Google таблицу
    save_to_sheet(user_data)
    await message.answer("Траты записаны.",
                         reply_markup=types.ReplyKeyboardRemove()
                         )
    await message.bot.send_message(os.getenv('CHAT_ID'),
                                   text=get_text(user_data)
                                   )
    # очищает данные состояния
    await state.finish()
    await message.answer(
            'Запиши свои траты:',
            reply_markup=types.ReplyKeyboardRemove()
            )


# Сгенерировать сообщение о тратах в чат
def get_text(data):
    value = data['value']
    currency = data['currency'].lower()
    category = data['category'].lower()
    return f"{value} {currency} потрачено на {category}."


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
