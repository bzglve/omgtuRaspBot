from aiogram.dispatcher.filters.state import State, StatesGroup


class BotStates(StatesGroup):
    WAIT_FOR_GROUP = State()
    WAIT_FOR_DATE = State()
