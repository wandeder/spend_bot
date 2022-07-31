import asyncio
import os
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from spend_bot.handlers import register_handlers_spend
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from spend_bot.commands import start, register_handlers_start


async def set_commands(bot: Bot):
    commands = [BotCommand(
        command="/restart",
        description="Запуск/рестарт бота-счетовода"
    )
    ]
    await bot.set_my_commands(commands)

async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.info("Starting bot")

    # загрузка переменных окружения из .env
    load_dotenv()

    # token from .env file
    API_TOKEN = os.getenv('API_TOKEN')

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    # register_handlers_start(dp)
    register_handlers_spend(dp)

    # Запуск бота
    await set_commands(bot)
    # Запуск поллинга
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())
