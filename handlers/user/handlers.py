import json
from datetime import date, datetime

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from database.base import change_group, get_user_group
from loader import bot, dp
from states.default import BotStates
from util.helpers import day_text, get_week_dates, lesson_text


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


@dp.message_handler(commands=["now"])
async def now_handler(msg: types.Message):
    user_group = get_user_group(msg.from_user.id)
    if user_group is None:
        await msg.answer("Сначала выберите группу\n(команда /group)")
        return

    today_date = date.today().strftime("%Y.%m.%d")
    if (
        request := requests.get(
            f"https://rasp.omgtu.ru/api/schedule/group/{user_group}?start={today_date}&finish={today_date}&lng=1"
        )
    ).text == "[]":
        return
    result = json.loads(request.text)

    current_time = datetime.now()
    current_time = datetime.strptime("18:21", "%H:%M")
    if lesson := list(
        filter(
            lambda lesson: datetime.strptime(lesson.get("beginLesson"), "%H:%M")
            <= current_time
            <= datetime.strptime(lesson.get("endLesson"), "%H:%M"),
            result,
        )
    ):
        schedule = lesson_text(lesson[0])

        await msg.answer(schedule, parse_mode=types.ParseMode.MARKDOWN)
    else:
        await msg.answer("Сейчас никаких пар не идет")


@dp.message_handler(commands=["next"])
async def next_handler(msg: types.Message):
    user_group = get_user_group(msg.from_user.id)
    if user_group is None:
        await msg.answer("Сначала выберите группу\n(команда /group)")
        return

    today_date = date.today().strftime("%Y.%m.%d")
    today_date = "2022.09.24"
    if (
        request := requests.get(
            f"https://rasp.omgtu.ru/api/schedule/group/{user_group}?start={today_date}&finish={today_date}&lng=1"
        )
    ).text == "[]":
        return
    result = json.loads(request.text)

    current_time = datetime.now()
    current_time = datetime.strptime("9:39", "%H:%M")

    if current_time < datetime.strptime(result[0].get("beginLesson"), "%H:%M"):
        lesson = [result[0]]
    else:
        current_lesson = False
        lesson = []
        for tmp_lesson in result:
            if (
                datetime.strptime(tmp_lesson.get("beginLesson"), "%H:%M")
                <= current_time
                <= datetime.strptime(tmp_lesson.get("endLesson"), "%H:%M")
            ):
                current_lesson = True
                continue
            if current_lesson:
                lesson.append(tmp_lesson)

    if lesson:
        schedule = lesson_text(lesson[0])

        await msg.answer(schedule, parse_mode=types.ParseMode.MARKDOWN)
    else:
        await msg.answer("Дальше никаких пар не идет")


@dp.message_handler(commands=["today"])
async def today_handler(msg: types.Message, ymd_date=None):
    user_group = get_user_group(msg.from_user.id)
    if user_group is None:
        await msg.answer("Сначала выберите группу\n(команда /group)")
        return

    today_date = ymd_date or date.today().strftime("%Y.%m.%d")
    if (
        request := requests.get(
            f"https://rasp.omgtu.ru/api/schedule/group/{user_group}?start={today_date}&finish={today_date}&lng=1"
        )
    ).text == "[]":
        return
    result = json.loads(request.text)
    with open(
        f"/home/god/Documents/omgtuRaspBot/{result[0].get('dayOfWeekString')}.json", "w"
    ) as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    schedule = (
        f"{ymd_date} ({result[0].get('dayOfWeekString')})\n" if ymd_date else ""
    ) + day_text(result)

    await msg.answer(schedule, parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=["week"])
async def week_handler(msg: types.Message, ymd_date=None):
    user_group = get_user_group(msg.from_user.id)
    if user_group is None:
        await msg.answer("Сначала выберите группу\n(команда /group)")
        return

    t = datetime.strptime(ymd_date, "%Y.%m.%d") if ymd_date else date.today()
    week = get_week_dates(t, 1, 7)

    for day in week:
        await today_handler(msg, day.strftime("%Y.%m.%d"))


@dp.message_handler(commands=["search_day"])
async def search_day_handler(msg: types.Message, state: FSMContext):
    # TODO получить день по инлайн-календарю
    # TODO получение только по дате (без месяца)
    await msg.answer(
        'По какой дате будем искать?\n(Введите дату в формате "дата.месяц", год необязательно)'
    )
    await BotStates.WAIT_FOR_DATE.set()
    async with state.proxy() as data:
        data["date_for"] = "day"


@dp.message_handler(commands=["search_week"])
async def search_day_handler(msg: types.Message, state: FSMContext):
    # TODO получить неделю по инлайн-календарю
    # TODO получение только по дате (без месяца)
    await msg.answer(
        'По какой дате будем искать?\n(Введите дату в формате "дата.месяц", год необязательно)'
    )
    await BotStates.WAIT_FOR_DATE.set()
    async with state.proxy() as data:
        data["date_for"] = "week"


@dp.message_handler(state=BotStates.WAIT_FOR_DATE)
async def wait_for_date_handler(msg: types.Message, state: FSMContext):
    try:
        request_date = datetime.strptime(
            f"{msg.text}.{date.today().year}", "%d.%m.%Y"
        ).strftime("%Y.%m.%d")
        target = ""
        async with state.proxy() as data:
            target = data.get("date_for")
        match target:
            case "day":
                await today_handler(msg, request_date)
            case "week":
                await week_handler(msg, request_date)
        await dp.current_state(user=msg.from_user.id).reset_state()
    except ValueError:
        await msg.answer('Я попросил вас в формате "дата.месяц"')


# ? посмотреть aiogram-dialog
# TODO отправление дня/недели по заданному расписанию (задать день, время, периодичность)
# TODO json -> sqlite.db
