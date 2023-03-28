import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram_dialog import DialogRegistry

from configs.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()

loop = asyncio.get_event_loop()
dp = Dispatcher(bot, storage=storage, loop=loop)

registry = DialogRegistry(dp)

dp.middleware.setup(LoggingMiddleware())
