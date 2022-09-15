from aiogram import types


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
                "week",
                "Получить расписание на текущую неделю",
            ),
            types.BotCommand("cancel", "Отмена"),
        ]
    )
