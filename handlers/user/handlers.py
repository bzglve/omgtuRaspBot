import json
from datetime import date, datetime, timedelta

import requests
from aiogram import types
# from aiogram.dispatcher import FSMContext
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog.widgets.text import Const

from database.base import change_group, get_user_group
from loader import bot, dp, registry
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
    change_group(callback.from_user.id, int(callback.data))
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

    schedule = (
        f"{ymd_date} ({result[0].get('dayOfWeekString')})\n" if ymd_date else ""
    ) + day_text(result)

    await bot.send_message(
        chat_id=msg.from_user.id, text=schedule, parse_mode=types.ParseMode.MARKDOWN
    )


@dp.message_handler(commands=["tomorrow"])
async def tomorrow_handler(msg: types.Message, ymd_date=None):
    user_group = get_user_group(msg.from_user.id)
    if user_group is None:
        await msg.answer("Сначала выберите группу\n(команда /group)")
        return

    # tomorrow_date = ymd_date or date.today().strftime("%Y.%m.%d")
    tomorrow_date = ymd_date or (date.today() + timedelta(days=1)).strftime("%Y.%m.%d")
    if (
        request := requests.get(
            f"https://rasp.omgtu.ru/api/schedule/group/{user_group}?start={tomorrow_date}&finish={tomorrow_date}&lng=1"
        )
    ).text == "[]":
        return
    result = json.loads(request.text)

    schedule = (
        f"{ymd_date} ({result[0].get('dayOfWeekString')})\n" if ymd_date else ""
    ) + day_text(result)

    await bot.send_message(
        chat_id=msg.from_user.id, text=schedule, parse_mode=types.ParseMode.MARKDOWN
    )


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


async def on_date_selected(
    c: types.CallbackQuery, widget, manager: DialogManager, selected_date: date
):
    msg = c.message
    msg.text = selected_date.strftime("%d.%m")
    print(msg)

    await wait_for_date_handler(msg)


calendar = Calendar(id="calendar", on_click=on_date_selected)
calendar_window = Window(
    Const(
        'По какой дате будем искать?\n(Введите дату в формате "дата.месяц" или выберите нужную в календаре)'
    ),
    calendar,
    state=BotStates.WAIT_FOR_DATE,
)
dialog = Dialog(calendar_window)


@dp.message_handler(commands=["search_day", "search_week"])
async def search_day_handler(msg: types.Message, dialog_manager: DialogManager):
    print(msg)
    # TODO починить состояние при выборе через календарь
    # TODO сейчас работает чисто на день, а надо и на день и на неделю
    # TODO получение только по дате (без месяца)
    await BotStates.WAIT_FOR_DATE.set()
    async with dp.current_state(
        chat=msg.chat.id, user=msg.from_user.id
    ).proxy() as data:
        data["date_for"] = msg.get_command().split("_")[-1]

    registry.register(dialog)
    await dialog_manager.start(BotStates.WAIT_FOR_DATE, mode=StartMode.RESET_STACK)


@dp.message_handler(state=BotStates.WAIT_FOR_DATE)
async def wait_for_date_handler(msg: types.Message):
    try:
        request_date = datetime.strptime(
            f"{msg.text}.{date.today().year}", "%d.%m.%Y"
        ).strftime("%Y.%m.%d")
        target = ""
        async with dp.current_state(
            chat=msg.chat.id, user=msg.from_user.id
        ).proxy() as data:
            target = data.get("date_for")
        match target:
            case "day":
                print(f"TODAY WITH {request_date}")
                await today_handler(msg, request_date)
            case "week":
                print(f"WEEK WITH {request_date}")
                await week_handler(msg, request_date)
        await dp.current_state(user=msg.from_user.id).reset_state()
    except ValueError:
        await msg.answer('Я попросил вас в формате "дата.месяц"')


# ? посмотреть aiogram-dialog
# TODO отправление дня/недели по заданному расписанию (задать день, время, периодичность)
# TODO json -> sqlite.db
