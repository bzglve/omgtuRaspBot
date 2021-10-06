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

start_commands = [
    'start',
    'help'
]

other_commands = [
    ''
]


@dp.message_handler(commands=start_commands)
async def send_welcome(msg: types.Message):
    await msg.answer('Приветствую\n\
Я бот расписания омского политеха\n\
Пока что довольно тупой, но разрабы постепенно меня прокачают')


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    await msg.answer('Да падажжи падла, я ещё них** не умею')


def main():
    ex.start_polling(dp)


if __name__ == '__main__':
    main()
