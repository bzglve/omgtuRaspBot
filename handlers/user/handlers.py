import locale
from datetime import date, datetime, timedelta
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import link
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Calendar
from aiogram_dialog.widgets.text import Const

from database.base import change_group, get_user_group
from keyboards.inline import get_groups_kb
from loader import bot, registry
from logger import logger
from states.default import DateSelect, GroupSelect, WeekSelect
from util.api import get_day_schedule, get_groups, get_week_schedule
from util.helpers import day_text, get_week_dates, lesson_text

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

event_actions = {}


def event_action(event_id, description=None):
    def register(func):
        event_actions[event_id] = {}
        event_actions[event_id]["func"] = func
        event_actions[event_id]["description"] = description
        return func

    return register


# /group
async def group_select_handler(msg: types.Message):
    await GroupSelect.waiting_for_group.set()
    await msg.answer("Введите название вашей группы, а я попытаюсь найти её")


async def wait_for_group_handler(msg: types.Message, state: FSMContext):
    try:
        groups = get_groups(msg.text)
    except ValueError:
        await msg.answer(
            f"""Я не смог найти группу по запросу \"{msg.text}\"
Попробуйте ещё раз
        """
        )
        return
    except Exception:
        await msg.answer(
            f"""Возникла непредвиденная ошибка
Попробуйте ещё раз или напишите {link('автору', 'https://t.me/bzglve')} об этой ошибке
        """,
            parse_mode=types.ParseMode.MARKDOWN,
        )
        return

    # check if query is already found
    if len(groups) == 1:
        group_id = groups[0]["id"]
        change_group(msg.chat.id, group_id)
        await state.finish()
        await state.reset_state()
        await msg.answer(f"Выбрана группа {groups[0]['label']}")
        return

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
    change_group(callback.message.chat.id, group_id)

    await callback.answer()

    event = await state.get_data()
    await state.finish()
    await state.reset_state()

    group_name = list(
        filter(lambda group: group["id"] == group_id, event["groups_list"])
    )[0].get("label")

    await callback.message.edit_text(f"Выбрана группа {group_name}")


################


@event_action(0)
async def now_handler(msg: types.Message):
    if not (group_id := get_user_group(msg.chat.id)):
        await bot.send_message(
            msg.chat.id,
            """Сначала выберите группу
(команда /group)""",
        )
        return

    today_date = date.today()
    try:
        schedule = get_day_schedule(group_id, today_date)
    except ValueError:
        await msg.answer("Сегодня нет пар")
        return
    except Exception:
        await msg.answer(
            f"""Возникла непредвиденная ошибка
Попробуйте ещё раз или напишите {link('автору', 'https://t.me/bzglve')} об этой ошибке
        """,
            parse_mode=types.ParseMode.MARKDOWN,
        )
        return

    current_time = datetime.now()

    if lesson := list(
        filter(
            lambda lesson: (
                datetime.strptime(
                    f'{lesson.get("date")} {lesson.get("beginLesson")}',
                    "%Y.%m.%d %H:%M",
                )
                <= current_time
                <= datetime.strptime(
                    f'{lesson.get("date")} {lesson.get("endLesson")}', "%Y.%m.%d %H:%M"
                )
            ),
            schedule,
        )
    ):
        schedule_text = lesson_text(lesson[0])

        await bot.send_message(
            msg.chat.id, schedule_text, parse_mode=types.ParseMode.MARKDOWN
        )
    else:
        await bot.send_message(msg.chat.id, "Сейчас никаких пар не идет")


@event_action(1)
async def next_handler(msg: types.Message):
    if not (group_id := get_user_group(msg.chat.id)):
        await bot.send_message(
            msg.chat.id,
            """Сначала выберите группу
(команда /group)"""
        )
        return

    today_date = date.today()
    try:
        schedule = get_day_schedule(group_id, today_date)
    except ValueError:
        await msg.answer("Сегодня нет пар")
        return
    except Exception:
        await msg.answer(
            f"""Возникла непредвиденная ошибка
Попробуйте ещё раз или напишите {link('автору', 'https://t.me/bzglve')} об этой ошибке
        """,
            parse_mode=types.ParseMode.MARKDOWN,
        )
        return

    current_time = datetime.now()

    if current_time < datetime.strptime(
        f'{schedule[0].get("date")} {schedule[0].get("beginLesson")}', "%Y.%m.%d %H:%M"
    ):
        lesson = [schedule[0]]
    else:
        current_lesson = False
        lesson = []
        for tmp_lesson in schedule:
            if (
                datetime.strptime(
                    f'{tmp_lesson.get("date")} {tmp_lesson.get("beginLesson")}',
                    "%Y.%m.%d %H:%M",
                )
                <= current_time
                <= datetime.strptime(
                    f'{tmp_lesson.get("date")} {tmp_lesson.get("endLesson")}',
                    "%Y.%m.%d %H:%M",
                )
            ):
                current_lesson = True
                continue
            if current_lesson:
                lesson.append(tmp_lesson)

    if lesson:
        schedule_text = lesson_text(lesson[0])

        await bot.send_message(msg.chat.id, schedule_text, parse_mode=types.ParseMode.MARKDOWN)
    else:
        await bot.send_message(msg.chat.id, "Сегодня больше нет пар")


@event_action(2)
async def today_handler(
    msg: types.Message, requested_date: date = None, schedule: list[dict] = None
):
    no_schedule = False
    if not schedule:
        if not (group_id := get_user_group(msg.chat.id)):
            await msg.answer(
                """Сначала выберите группу
(команда) /group"""
            )
            return

        d = requested_date or date.today()

        try:
            schedule = get_day_schedule(group_id, d)
        except ValueError:
            no_schedule = True
        except Exception:
            await msg.answer(
                f"""Возникла непредвиденная ошибка
Попробуйте ещё раз или напишите {link('автору', 'https://t.me/bzglve')} об этой ошибке
        """,
                parse_mode=types.ParseMode.MARKDOWN,
            )
            return
    else:
        d = datetime.strptime(schedule[0].get("date"), "%Y.%m.%d")

    text_format = """
{date} ({short_date})
{text}
    """

    text = text_format.format(
        **{
            "date": d.strftime("%d.%m"),
            "short_date": d.strftime("%a"),
            "text": "Нет пар" if no_schedule else day_text(schedule),
        }
    )
    await bot.send_message(msg.chat.id, text, types.ParseMode.MARKDOWN)


@event_action(3)
async def tomorrow_handler(msg: types.Message, ymd_date=None):
    tomorrow_date = ymd_date or (date.today() + timedelta(days=1))
    await today_handler(msg, tomorrow_date)


async def week_handler(msg: types.Message, ymd_date: date = None):
    if not (group_id := get_user_group(msg.chat.id)):
        await msg.answer(
            """Сначала выберите группу
(команда /group)"""
        )
        return

    t = ymd_date or date.today()
    week = get_week_dates(t, 1, 7)

    try:
        schedule = get_week_schedule(group_id, week[0], week[-1])
    except ValueError:
        await msg.answer("На этой неделе не найдено пар")
        return

    for day in schedule:
        await today_handler(msg, schedule=day)


async def on_day_selected(
    c: types.CallbackQuery, widget, manager: DialogManager, selected_date: date
):
    logger.debug("on_date_selected")
    await c.answer()
    await c.message.answer(str(selected_date))

    await c.message.delete()

    await manager.done()

    await today_handler(c.message, selected_date)


async def on_week_selected(
    c: types.CallbackQuery, widget, manager: DialogManager, selected_date: date
):
    logger.debug("on_date_selected")
    await c.answer()
    await c.message.answer(str(selected_date))

    await c.message.delete()

    await manager.done()

    await week_handler(c.message, selected_date)


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


async def search_day_handler(msg: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(DateSelect.wait_for_day, mode=StartMode.RESET_STACK)


async def search_week_handler(msg: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(WeekSelect.wait_for_week, mode=StartMode.RESET_STACK)


# TODO 
# [ ] отправление дня/недели по заданному расписанию (задать день, время, периодичность)
# [ ] json -> sqlite.db
