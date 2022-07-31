from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# Names categories of spending and names currency
categories_names = ['Еда', 'Транспорт', 'Крупные покупки',
                    'Жилье', 'Другое', 'Доходы']
currency_names = ['Лиры', 'Рубли', 'Доллары', 'Евро']


class RegisterSpend(StatesGroup):
    waiting_money = State()
    waiting_currency = State()
    waiting_category = State()


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


async def chose_currency(message: types.Message, state: FSMContext):
    if message.text not in currency_names:
        await message.answer('Выбери валюту, я сказал!')
        return
    await state.update_data(currency=message.text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for category in categories_names:
        keyboard.add(category)
    await RegisterSpend.waiting_category.set()
    await message.answer('Теперь выбери категорию трат:',
                         reply_markup=keyboard)


async def chose_category(message: types.Message, state: FSMContext):
    if message.text not in categories_names:
        await message.answer('Выбери уже категорию!')
        return
    await state.update_data(category=message.text)
    # данные записи траты для записи в таблицу
    user_data = await state.get_data()
    await message.answer(f"""Твои траты: {user_data} записаны.\n"""
                          """Постарайся тратить меньше!""",
                         reply_markup=types.ReplyKeyboardRemove()
                        )
    # очищает данные состояния
    await state.finish()
    await message.answer(
            'Запиши свои траты:',
            reply_markup=types.ReplyKeyboardRemove()
            )


def register_handlers_spend(dp: Dispatcher):
    dp.register_message_handler(start_bot)
    dp.register_message_handler(chose_currency,
                                state=RegisterSpend.waiting_currency)
    dp.register_message_handler(chose_category,
                                state=RegisterSpend.waiting_category)
