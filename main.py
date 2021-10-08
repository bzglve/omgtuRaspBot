import json
import re

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor as ex
from requests import get

from private_variables import BOT_TOKEN

variables_file = 'variables.json'
page_url = 'https://rasp.omgtu.ru/api/schedule/group/'

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

bot_ban_usernames = [
]


days_of_week = [
    'Пн',
    'Вт',
    'Ср',
    'Чт',
    'Пт',
    'Сб'
]


async def choose_group(msg: types.Message):
    group = '-'.join(re.split('\W+', msg.text)[1:])
    with open(variables_file, 'r') as f:
        group_id = dict(json.load(f))[group]
    group_shedule_raw = get(page_url + str(group_id))
    group_shedule = json.loads(group_shedule_raw.content.decode('utf-8'))
    for day_of_week in days_of_week:
        await msg.answer(f'{day_of_week}')
        for s in group_shedule:
            if s['dayOfWeekString'] == day_of_week:
                await msg.answer(f"{s['discipline']}\n{s['auditorium']}\n{s['beginLesson']}-{s['endLesson']}\n{s['lecturer']}")

    # re.split('\W+', master_keys_raw)


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    if msg.from_user.username in bot_ban_usernames:
        await msg.answer(f'{msg.from_user.first_name}, иди нахуй, че доебался до меня?')
    else:
        await msg.answer('Приветствую\n\
Я бот расписания омского политеха\n\
Пока что довольно тупой, но разрабы постепенно меня прокачают')


@dp.message_handler(commands=['help'])
async def send_help(msg: types.Message):
    if msg.from_user.username in bot_ban_usernames:
        await msg.answer(f'{msg.from_user.first_name}, иди нахуй, че доебался до меня?')
    else:
        await msg.answer('/groups Выведет список всех групп')


@dp.message_handler(commands=['group'])
async def choose_group_help(msg: types.Message):
    if msg.from_user.username in bot_ban_usernames:
        await msg.answer(f'{msg.from_user.first_name}, иди нахуй, че доебался до меня?')
    else:
        await msg.answer('Напиши пожлуйста номер своей группы в формате "Группа ..."')
        await msg.answer('Например "Группа БИТ-201"')


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    print(msg)
    print(msg.text.lower())
    if msg.from_user.username in bot_ban_usernames:
        await msg.answer(f'{msg.from_user.first_name}, иди нахуй, че доебался до меня?')
    else:
        try:
            if 'Группа' in msg.text:
                await bot_commands_keys['Группа'](msg)
            else:
                await bot_commands_keys[msg.text](msg)
        except KeyError:
            await msg.answer(f'Я пока что знаю только комманды "{", ".join(list(bot_commands_keys.keys()))}"')
            await msg.answer('Да падажжи падла, я ещё них** не умею')


bot_commands_keys = {
    'Справка': send_help,
    'Выбор группы': choose_group_help,
    'Группа': choose_group
}


def main():
    ex.start_polling(dp)


if __name__ == '__main__':
    main()

# TODO дописать дохуя функционала
