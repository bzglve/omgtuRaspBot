from aiogram import types
from loader import dp
from aiogram.utils.markdown import link


@dp.message_handler(commands=["cancel"], state="*")
async def cancel_handler(msg: types.Message):
    await dp.current_state(user=msg.from_user.id).reset_state()


@dp.message_handler(commands=["start"])
async def start_handler(msg: types.Message):
    await msg.answer(
        "Приветствую\nЯ бот с расписанием Омского политеха (ОмГТУ)\nЕсли вдруг вы найдёте баг или у вас есть предложения по развитию, напишите в лс @bzglve"
    )
    await msg.answer(
        "Слева от поля для ввода находится меню с коммандами, которые я умею исполнять\nДля начала попробуйте команду /group"
    )


@dp.message_handler(commands=["help"])
async def help_handler(msg: types.Message):
    text = link("github", "https://github.com/viktory683/omgtuRaspBot")
    await msg.answer("Всё, что вам может понадобится находится в меню комманд")
    await msg.answer(text, parse_mode=types.ParseMode.MARKDOWN)
