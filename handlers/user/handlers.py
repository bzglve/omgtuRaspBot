import json
from datetime import date, datetime, timedelta
from urllib.parse import urlencode

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog.widgets.text import Const

from database.base import change_group, get_user_group
from keyboards.inline import get_groups_kb
from loader import bot, logger, registry
from states.default import DateSelect, GroupSelect, WeekSelect
from util.helpers import day_text, get_week_dates, lesson_text


async def group_select_handler(msg: types.Message):
    await GroupSelect.waiting_for_group.set()
    await msg.answer("Введите название вашей группы, а я попытаюсь найти её")


async def wait_for_group_handler(msg: types.Message, state: FSMContext):
    result = requests.get(
        f"https://rasp.omgtu.ru/api/search?term={msg.text}&type=group"
    )
    groups = json.loads(result.text)
    await state.update_data(groups_list=groups)

    await msg.answer(
        """Выбери среди указанных ниже групп свою
Либо попробуй ввести запрос ещё раз""",
        reply_markup=get_groups_kb(
            list(
                map(
                    lambda group: {"name": group.get("label"), "id": group.get("id")},
                    groups,
                )
            )
        ),
    )


async def handle_group_callback(callback: types.CallbackQuery, state=FSMContext):
    group_id = int(callback.data)
    change_group(callback.from_user.id, group_id)

    await callback.answer()

    event = await state.get_data()
    await state.finish()
    await state.reset_state()

    group_name = list(
        filter(lambda group: group["id"] == group_id, event["groups_list"])
    )[0].get("label")

    await callback.message.edit_text(f"Выбрана группа {group_name}")


async def now_handler(msg: types.Message):
    user_group = get_user_group(msg.from_user.id)
    if user_group is None:
        await msg.answer(
            """Сначала выберите группу
(команда /group)"""
        )
        return

    today_date = date.today().strftime("%Y.%m.%d")
    params = {"start": today_date, "finish": today_date, "lng": 1}
    if (
        request := requests.get(
            f"https://rasp.omgtu.ru/api/schedule/group/{user_group}?{urlencode(params)}"
        )
    ).text == "[]":
        return
    result = json.loads(request.text)

    current_time = datetime.now()

    if lesson := list(
        filter(
            lambda lesson: (
                datetime.strptime(lesson.get("beginLesson"), "%H:%M")
                <= current_time
                <= datetime.strptime(lesson.get("endLesson"), "%H:%M")
            ),
            result,
        )
    ):
        schedule = lesson_text(lesson[0])

        await msg.answer(schedule, parse_mode=types.ParseMode.MARKDOWN)
    else:
        await msg.answer("Сейчас никаких пар не идет")


async def next_handler(msg: types.Message):
    user_group = get_user_group(msg.from_user.id)
    if user_group is None:
        await msg.answer("Сначала выберите группу\n(команда /group)")
        return

    today_date = date.today().strftime("%Y.%m.%d")
    params = {
        "start": today_date,
        "finish": today_date,
        "lng": 1,
    }
    if (
        request := requests.get(
            f"https://rasp.omgtu.ru/api/schedule/group/{user_group}?{urlencode(params)}"
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
        await msg.answer("Сегодня больше нет пар")


async def today_handler(msg: types.Message, ymd_date=None):
    user_group = get_user_group(msg.chat.id)
    if user_group is None:
        await msg.answer(
            """Сначала выберите группу
(команда /group)"""
        )
        return

    today_date = ymd_date or date.today().strftime("%Y.%m.%d")
    params = {"start": today_date, "finish": today_date, "lng": 1}
    if (
        request := requests.get(
            f"https://rasp.omgtu.ru/api/schedule/group/{user_group}?{urlencode(params)}"
        )
    ).text == "[]":
        await bot.send_message(msg.chat.id, "Нет пар")
        return
    result = json.loads(request.text)

    schedule = (
        f"{ymd_date} ({result[0].get('dayOfWeekString')})\n" if ymd_date else ""
    ) + day_text(result)

    await bot.send_message(
        chat_id=msg.chat.id, text=schedule, parse_mode=types.ParseMode.MARKDOWN
    )


async def tomorrow_handler(msg: types.Message, ymd_date=None):
    user_group = get_user_group(msg.from_user.id)
    if user_group is None:
        await msg.answer(
            """Сначала выберите группу
(команда /group)"""
        )
        return

    tomorrow_date = ymd_date or (date.today() + timedelta(days=1)).strftime("%Y.%m.%d")
    params = {"start": tomorrow_date, "finish": tomorrow_date, "lng": 1}
    if (
        request := requests.get(
            f"https://rasp.omgtu.ru/api/schedule/group/{user_group}?{urlencode(params)}"
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


async def week_handler(msg: types.Message, ymd_date=None):
    user_group = get_user_group(msg.chat.id)
    if user_group is None:
        await msg.answer(
            """Сначала выберите группу
(команда /group)"""
        )
        return

    t = datetime.strptime(ymd_date, "%Y.%m.%d") if ymd_date else date.today()
    week = get_week_dates(t, 1, 7)

    for day in week:
        await today_handler(msg, day.strftime("%Y.%m.%d"))


async def on_day_selected(
    c: types.CallbackQuery, widget, manager: DialogManager, selected_date: date
):
    logger.debug("on_date_selected")
    await c.answer()
    await c.message.answer(str(selected_date))

    await c.message.delete()

    await manager.done()

    await today_handler(c.message, selected_date.strftime("%Y.%m.%d"))


async def on_week_selected(
    c: types.CallbackQuery, widget, manager: DialogManager, selected_date: date
):
    logger.debug("on_date_selected")
    await c.answer()
    await c.message.answer(str(selected_date))

    await c.message.delete()

    await manager.done()

    await week_handler(c.message, selected_date.strftime("%Y.%m.%d"))


day_window = Window(
    Const("Выберите дату из календаря"),
    Calendar(id="calendar", on_click=on_day_selected),
    state=DateSelect.wait_for_day,
)
day_dialog = Dialog(day_window)
registry.register(day_dialog)

week_window = Window(
    Const("Выберите дату из календаря"),
    Calendar(id="calendar", on_click=on_week_selected),
    state=WeekSelect.wait_for_week,
)
week_dialog = Dialog(week_window)
registry.register(week_dialog)


# @dp.message_handler(commands=["search_day"])
async def search_day_handler(msg: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(DateSelect.wait_for_day, mode=StartMode.RESET_STACK)


# @dp.message_handler(commands=["search_week"])
async def search_week_handler(msg: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(WeekSelect.wait_for_week, mode=StartMode.RESET_STACK)


# TODO отправление дня/недели по заданному расписанию (задать день, время, периодичность)
# TODO json -> sqlite.db
