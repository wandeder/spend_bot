import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from spend_bot.location import get_location_reply
from spend_bot.sheets import save_to_sheet


load_dotenv()

bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

CATEGORIES = [category.strip() for category in os.environ.get("CATEGORIES", "").split(",")]
CURRENCIES = [currency.strip() for currency in os.environ.get("CURRENCIES", "").split(",")]
BANKS = [bank.strip() for bank in os.environ.get("BANKS", "").split(",")]


class RegisterSpend(StatesGroup):
    waiting_money = State()
    waiting_currency = State()
    waiting_category = State()
    waiting_comment = State()
    waiting_record = State()
    waiting_bank = State()


@dp.message_handler(commands='start', state='*')
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
            'Запиши свои траты:',
            reply_markup=types.ReplyKeyboardRemove(),
            )


@dp.message_handler(commands='country', state='*')
async def country(message: types.Message, state: FSMContext):
    await state.finish()
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    await message.answer(
            'Поделись своей локацией:',
            reply_markup=keyboard.add(types.KeyboardButton("Share location", request_location=True))
            )


@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    await message.answer(get_location_reply(message.location), reply_markup=types.ReplyKeyboardRemove())


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
        for name in CURRENCIES:
            keyboard.add(name)
        await RegisterSpend.waiting_currency.set()
        await message.answer("Выбери валюту:", reply_markup=keyboard)


@dp.message_handler(state=RegisterSpend.waiting_currency)
async def choose_currency(message: types.Message, state: FSMContext):
    if message.text not in CURRENCIES:
        await message.answer('Выбери валюту!')
        return

    await state.update_data(currency=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in CATEGORIES:
        keyboard.add(category)
    await RegisterSpend.waiting_category.set()
    await message.answer(
            'Теперь выбери категорию трат:',
            reply_markup=keyboard,
            )


@dp.message_handler(state=RegisterSpend.waiting_category)
async def choose_category(message: types.Message, state: FSMContext):
    if message.text not in CATEGORIES:
        await message.answer('Выбери категорию!')
        return

    await state.update_data(category=message.text)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for bank in BANKS:
        keyboard.add(bank)

    await RegisterSpend.waiting_bank.set()

    await message.answer(
        'Выбери банк:',
        reply_markup=keyboard,
    )


@dp.message_handler(state=RegisterSpend.waiting_bank)
async def choose_bank(message: types.Message, state: FSMContext):
    if message.text not in BANKS:
        await message.answer('Выбери банк!')
        return

    await state.update_data(bank=message.text)

    await RegisterSpend.waiting_comment.set()

    await message.answer(
            'Введи комментарий:',
            reply_markup=types.ReplyKeyboardRemove(),
            )


@dp.message_handler(state=RegisterSpend.waiting_comment)
async def comment(message: types.Message, state: FSMContext):
    await state.update_data(comment=message.text)

    # Get data
    data = await state.get_data()
    # Restart bot
    await start(message, state)
    # Write data into Google Sheet and chat
    await message.bot.send_message(os.getenv('CHAT_ID'),
                                   text=get_text(data)
                                   )
    await save_to_sheet(data)


def get_text(data):
    return (f"{data.get('value')} {data.get('currency').lower()} потрачено на {data.get('category').lower()}."
            f" {data.get('comment')}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
