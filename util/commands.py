from aiogram import types

from handlers.default import setup as default_setup
from handlers.user import setup as user_setup


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
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
                "search_week",
                "Поиск расписания на неделю по дате",
            ),
            types.BotCommand(
                "search_day",
                "Поиск расписания на день по дате",
            ),
            types.BotCommand("cancel", "Отмена"),
        ]
    )


def register_handlers(dispatcher):
    default_setup(dispatcher)
    user_setup(dispatcher)
