from aiogram.dispatcher.filters.state import State, StatesGroup


class GroupSelect(StatesGroup):
    waiting_for_group = State()


class DateSelect(StatesGroup):
    wait_for_day = State()


class WeekSelect(StatesGroup):
    wait_for_week = State()
