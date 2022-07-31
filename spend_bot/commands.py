from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, IDFilter


async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
            'Запиши свои траты:',
            reply_markup=types.ReplyKeyboardRemove()
            )


def register_handlers_start(dp: Dispatcher):
    dp.register_message_handler(start,
                                commands="restart",
                                state="*")
