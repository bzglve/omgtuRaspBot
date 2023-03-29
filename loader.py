import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram_dialog import DialogRegistry

from config.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
registry = DialogRegistry(dp)

dp.middleware.setup(LoggingMiddleware())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot")
logger.setLevel(logging.DEBUG)
