import json

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor as ex

variables_file = 'variables.json'
private_variables_file = 'private_variables.json'

with open(private_variables_file, 'r') as pv:
    BOT_TOKEN = json.load(pv)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

bot_commands_keys = {
    ''
    'Выбор группы'
}


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    keys = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keys.add(types.KeyboardButton())
    await msg.answer('Приветствую\n\
Я бот расписания омского политеха\n\
Пока что довольно тупой, но разрабы постепенно меня прокачают', reply_markup=keys)


@dp.message_handler(commands=['help'])
async def send_help(msg: types.Message):
    await msg.answer('/groups Выведет список всех групп')


@dp.message_handler(commands=['group'])
async def send_groups(msg: types.Message):
    await msg.answer('Напиши номер своей группы')
    await msg.answer('Например "БИТ-201...')


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    print(msg)
    print(msg.text.lower())
    if 'да' == msg.text.lower():
        await msg.answer('Ну я тебя предупреждал')
        with open('variables.json', 'r') as f:
            groups = list(dict(json.load(f)).keys())
            await msg.answer((' '.join(groups))[:4096])
            await msg.answer((' '.join(groups))[4096:4096 * 2])
    else:
        await msg.answer('Да падажжи падла, я ещё них** не умею')


def main():
    ex.start_polling(dp)


if __name__ == '__main__':
    main()

# TODO дописать дохуя функционала
