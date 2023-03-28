from aiogram import types
from aiogram.utils.markdown import link

from loader import dp
from logger import logger


async def cancel_handler(msg: types.Message):
    await dp.current_state(user=msg.from_user.id).reset_state()


async def start_handler(msg: types.Message):
    logger.info(f"New user msg: {msg}")
    await msg.answer(
        """Приветствую
Я бот с расписанием Омского политеха (ОмГТУ)
Если вдруг вы найдёте баг или у вас есть предложения по развитию, напишите в лс @bzglve"""
    )
    await msg.answer(
        """Слева от поля для ввода находится меню с командами, которые я умею выполнять
Для начала попробуйте команду /group"""
    )


async def help_handler(msg: types.Message):
    text = link("github", "https://github.com/viktory683/omgtuRaspBot")
    await msg.answer("Всё, что вам может понадобится находится в меню команд")
    await msg.answer(text, parse_mode=types.ParseMode.MARKDOWN)
