from aiogram import Dispatcher, types
from aiogram.utils.markdown import link

from handlers.default import setup as default_setup
from handlers.default.handlers import text_handler
from handlers.user import setup as user_setup

bot_commands = [
    types.BotCommand(
        "start",
        "Запустить бота",
    ),
    types.BotCommand(
        "help",
        "Справка",
    ),
    types.BotCommand(
        "group",
        "Выбрать группу",
    ),
    types.BotCommand(
        "today",
        "Получить расписание на сегодня",
    ),
    types.BotCommand(
        "tomorrow",
        "Получить расписание на завтра",
    ),
    types.BotCommand(
        "week",
        "Получить расписание на текущую неделю",
    ),
    types.BotCommand(
        "now",
        "Текущая пара",
    ),
    types.BotCommand(
        "next",
        "Следующая пара",
    ),
    types.BotCommand(
        "search_day",
        "Поиск расписания на день по дате",
    ),
    types.BotCommand(
        "search_week",
        "Поиск расписания на неделю по дате",
    ),
    types.BotCommand(
        "info",
        "Информация для информирования интересующихся",
    ),
    types.BotCommand("cancel", "Отмена (сброс состояния бота до начального)"),
]


async def set_default_commands(dp):
    await dp.bot.set_my_commands(bot_commands)


async def help_handler(msg: types.Message):
    await msg.answer(
        "\n".join(
            map(
                lambda command: f"/{command['command']}: {command['description']}",
                bot_commands,
            )
        )
    )
    await msg.answer(
        "Всё, что вам может понадобится находится в меню слева от строки ввода"
    )


async def info_handler(msg: types.Message):
    await msg.answer(
        f"Телеграм автора для жалоб и предложений {link('@bzglve', 'https://t.me/bzglve')}",
        parse_mode=types.ParseMode.MARKDOWN,
    )
    await msg.answer(
        f"Исходный код проекта {link('github', 'https://github.com/viktory683/omgtuRaspBot')}",
        parse_mode=types.ParseMode.MARKDOWN,
    )


def register_handlers(dispatcher: Dispatcher):
    default_setup(dispatcher)
    user_setup(dispatcher)
    dispatcher.register_message_handler(help_handler, commands=["help"], state="*")
    dispatcher.register_message_handler(info_handler, commands=["info"], state="*")
    dispatcher.register_message_handler(text_handler)
