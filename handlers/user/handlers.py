import json
from datetime import date

import requests
from aiogram import types
from database.base import change_group, get_user_group
from loader import bot, dp
from states.default import BotStates
from util.helpers import get_week_dates


@dp.message_handler(commands=["group"])
async def group_select_handler(msg: types.Message):
    await msg.answer("Введите название вашей группы, а я попытаюсь найти её")
    await BotStates.WAIT_FOR_GROUP.set()


@dp.message_handler(state=BotStates.WAIT_FOR_GROUP)
async def wait_for_group_handler(msg: types.Message):
    result = requests.get(
        f"https://rasp.omgtu.ru/api/search?term={msg.text}&type=group"
    )
    groups = json.loads(result.text)
    kb = types.InlineKeyboardMarkup().add(
        *list(
            map(
                lambda group: types.InlineKeyboardButton(
                    group.get("label"), callback_data=group.get("id")
                ),
                groups,
            )
        )
    )
    await msg.answer(
        "Выбери среди указанных ниже групп свою\nЛибо попробуй ввести запрос ещё раз",
        reply_markup=kb,
    )


@dp.callback_query_handler(state=BotStates.WAIT_FOR_GROUP)
async def handle_group_callback(callback: types.CallbackQuery):
    await bot.answer_callback_query(callback.id)
    change_group(callback.from_user.id, callback.data)
    await callback.message.delete()
    await bot.send_message(callback.message.chat.id, "Группа выбрана")
    await dp.current_state(user=callback.from_user.id).reset_state()


@dp.message_handler(commands=["today"])
async def today_handler(msg: types.Message, ymd_date=None):
    user_group = get_user_group(msg.from_user.id)
    if user_group is None:
        await msg.answer("Сначала выберите группу\n(команда /group)")
        return

    today_date = ymd_date or date.today().strftime("%Y.%m.%d")
    result = json.loads(
        requests.get(
            f"https://rasp.omgtu.ru/api/schedule/group/{user_group}?start={today_date}&finish={today_date}&lng=1"
        ).text
    )
    if result == []:
        return

    schedule = (f"{ymd_date}\n" if ymd_date else "") + "".join(
        f'*{lesson.get("beginLesson")}* *-* *{lesson.get("endLesson")}*        _{lesson.get("auditorium")}_\n{lesson.get("discipline")}\n{lesson.get("lecturer_rank")} {lesson.get("lecturer_title")}\n\n'
        for lesson in result
    )

    await msg.answer(schedule, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=["week"])
async def week_handler(msg: types.Message):
    user_group = get_user_group(msg.from_user.id)
    if user_group is None:
        await msg.answer("Сначала выберите группу\n(команда /group)")
        return

    t = date.today()
    week = get_week_dates(t, 1, 7)

    for day in week:
        await today_handler(msg, day.strftime("%Y.%m.%d"))


# ? посмотреть aiogram-dialog
# TODO получить день по дате (по запросу или с инлайн-календарем)
# TODO отправление дня/недели по заданному расписанию (задать день, время, периодичность)
# TODO получить расписание в текущее время (что идет сейчас, что будет следующим)
# TODO починить формат, если преподаватель - None, или что бы то ни было
# TODO json -> sqlite.db
