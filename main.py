import difflib
import json

import aiogram.utils.exceptions
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor as ex
from requests import get

from private_variables import BOT_TOKEN

variables_file = 'variables.json'
schedule_url = 'https://rasp.omgtu.ru/api/schedule/'
auditorium_url = schedule_url + 'auditorium/'
group_url = schedule_url + 'group/'
person_url = schedule_url + 'person/'

lesson_keys = {
    'auditorium',
    'auditoriumAmount',
    'auditoriumOid',
    'author',
    'beginLesson',
    'building',
    'buildingGid',
    'buildingOid',
    'contentOfLoadOid',
    'contentOfLoadUID',
    'contentTableOfLessonsName',
    'contentTableOfLessonsOid',
    'createddate',
    'date',
    'dateOfNest',
    'dayOfWeek',
    'dayOfWeekString',
    'detailInfo',
    'discipline',
    'disciplineOid',
    'disciplineinplan',
    'disciplinetypeload',
    'duration',
    'endLesson',
    'group',
    'groupOid',
    'groupUID',
    'group_facultyoid',
    'hideincapacity',
    'isBan',
    'kindOfWork',
    'kindOfWorkComplexity',
    'kindOfWorkOid',
    'kindOfWorkUid',
    'lecturer',
    'lecturerCustomUID',
    'lecturerEmail',
    'lecturerOid',
    'lecturerUID',
    'lecturer_rank',
    'lecturer_title',
    'lessonNumberEnd',
    'lessonNumberStart',
    'lessonOid',
    'listOfLecturers',
    'modifieddate',
    'note',
    'note_description',
    'parentschedule',
    'replaces',
    'stream',
    'streamOid',
    'stream_facultyoid',
    'subGroup',
    'subGroupOid',
    'subgroup_facultyoid',
    'tableofLessonsName',
    'tableofLessonsOid',
    'url1',
    'url1_description',
    'url2',
    'url2_description'
}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

admin_ids = {
    '389026886': 'bzglve',
    '700440368': 'rumbleofgunlock'
}

bot_ban_usernames = {}

weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']


# @dp.message_handler(content_types=['text'])
@dp.message_handler(commands=['info'])
@dp.message_handler(lambda msg: msg.text.split()[0] in commands['info'])
async def send_info(msg: types.Message):
    await msg.answer(f'Бот написан практически на чистом энтузиазме студентами КЗИ-191 в октябре 2021')
    await msg.answer(f"По всем вопросам обращаться {' '.join([('@' + admin) for admin in list(admin_ids.values())])}")


async def choose_group(msg: types.Message):
    group = msg.text[len(msg.text.split()[0]) + 1:]
    with open(variables_file, 'r') as f:
        groups = dict(json.load(f))
    try:
        group_id = groups[group]
        group_schedule_raw = get(group_url + str(group_id))
        group_schedule = json.loads(group_schedule_raw.content.decode('utf-8'))
        for weekday in weekdays:
            weekday_schedule = [lesson for lesson in group_schedule if
                                lesson['dayOfWeekString'] == weekday and not lesson['isBan']]
            wd_str = ''

            if len(weekday_schedule) > 0:
                wd_str += weekday + ' ' + weekday_schedule[0]['date'] + '\n'
            for lesson in weekday_schedule:
                discipline = f'{lesson["discipline"]}'
                time = f'{lesson["beginLesson"]} - {lesson["endLesson"]}'
                if lesson['subGroup']:
                    subGroup = f'({lesson["subGroup"]})'
                else:
                    subGroup = ''
                if 'В.А.' not in lesson['auditorium']:
                    auditorium = f'{lesson["auditorium"]}'
                else:
                    auditorium = ''
                try:
                    kindOfWork = f'{"".join([a[:1].upper() for a in lesson["kindOfWork"].split()])}'
                except AttributeError:
                    kindOfWork = lesson['kindOfWork']
                    print(lesson)
                lecturer = f'{lesson["lecturer"]}'

                wd_str += f'<b>{discipline} ({kindOfWork})</b>\n' \
                          f'    <i>{time}</i> {auditorium} {subGroup}\n' \
                          f'    {lecturer}\n'

            try:
                await msg.answer(wd_str, parse_mode='html')
            except aiogram.utils.exceptions.MessageTextIsEmpty:
                pass
    except KeyError:
        await msg.answer(f'Я хер знает, что это за группа')
        await msg.answer(f'Но похоже на {" или ".join(difflib.get_close_matches(group.upper(), groups))}')
        await msg.answer(f'Найди выше свою группу и введи в точности, как там написано')
        await msg.answer(f'Если выше такой группы нет, тогда пиши @bzglve, он всё починит')


@dp.message_handler(commands=['start'], user_id=admin_ids)
async def send_welcome(msg: types.Message):
    await msg.answer(f'Приветствую, {msg.from_user.full_name}')
    await msg.answer(f'Чего изволите, хозяин?')


@dp.message_handler(commands=['start'])
async def send_welcome(msg: types.Message):
    await msg.answer('Приветствую')
    await msg.answer('Я бот расписания омского политеха')
    await msg.answer('Пока что довольно тупой, но разрабы меня постоянно прокачивают')
    await msg.answer(f"Если есть вопросы по работе, жалобы или предложения по сотрудничеству, то можешь смело писать "
                     f"писать админу {', '.join([('@' + admin) for admin in list(admin_ids.values())[:1]])}")


@dp.message_handler(commands=['help'])
@dp.message_handler(lambda msg: msg.text.split()[0] in commands['help'])
async def send_help(msg: types.Message):
    for key in commands.keys():
        await msg.answer(f"{' '.join(commands[key]['commands'])}\n"
                         f"{commands[key]['comment']}")


@dp.message_handler(user_id=bot_ban_usernames)
async def handle_banned(msg: types.Message):
    print(f'@{msg.from_user.username}({msg.from_user.id}) пытался написать "{msg.text}"')
    await msg.answer(f'{msg.from_user.full_name}, ты в бане, пошел нахуй ютсюдова')


@dp.message_handler(commands=['group'])
async def choose_group_help(msg: types.Message):
    await msg.answer('Напиши пожлуйста номер своей группы в формате "Группа ..."')
    await msg.answer('Например "Группа БИТ-201"')


@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    print(msg)
    print(msg.text.lower())
    try:
        await commands_aliases[msg.text.lower().split()[0]](msg)
    except KeyError:
        await msg.answer(f'Я тебя не понял \n'
                         f'/help выведет список доступных комманд\n'
                         f'Ну либо ещё не умею отвечать на это')
        await msg.answer(f'Попробуй написать @{list(admin_ids.values())[0]} если возникли трудности')


commands = {
    'help': {
        'commands': {
            'help',
            'хелп',
            'справка'
        },
        'action': send_help,
        'comment': 'Помощь по коммандам'
    },
    'group': {
        'commands': {
            'group',
            'группа'
        },
        'action': choose_group,
        'comment': 'Выбор рабочей группы'
    },
    'info': {
        'commands': {
            'info',
            'информация',
            'инфо'
        },
        'action': send_info,
        'comment': 'Информация о боте'
    }
}

commands_aliases = {}


def main():
    def command_aliases_constructor():
        for key in commands.keys():
            for command in commands[key]['commands']:
                commands_aliases[command] = commands[key]['action']

    command_aliases_constructor()

    ex.start_polling(dp)


if __name__ == '__main__':
    main()

# TODO дописать дохуя функционала
