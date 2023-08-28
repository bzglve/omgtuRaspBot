from aiogram import Dispatcher
from config.config import AUTHOR

from handlers.user.handlers import (
    easter_egg_handler,
    group_select_handler,
    handle_group_callback,
    # new_notification_handler,
    next_handler,
    now_handler,
    search_day_handler,
    search_week_handler,
    today_handler,
    tomorrow_handler,
    wait_for_group_handler,
    week_handler,
)
from states.default import GroupSelect


def setup(dispatcher: Dispatcher):
    dispatcher.register_message_handler(group_select_handler, commands=["group"], state="*")
    dispatcher.register_message_handler(
        wait_for_group_handler, state=GroupSelect.waiting_for_group
    )
    dispatcher.register_callback_query_handler(
        handle_group_callback, state=GroupSelect.waiting_for_group
    )
    dispatcher.register_message_handler(now_handler, commands=["now"], state="*")
    dispatcher.register_message_handler(next_handler, commands=["next"], state="*")
    dispatcher.register_message_handler(today_handler, commands=["today"], state="*")
    dispatcher.register_message_handler(tomorrow_handler, commands=["tomorrow"], state="*")
    dispatcher.register_message_handler(week_handler, commands=["week"], state="*")
    dispatcher.register_message_handler(search_day_handler, commands=["search_day"], state="*")
    dispatcher.register_message_handler(search_week_handler, commands=["search_week"], state="*")
    # dispatcher.register_message_handler(new_notification_handler, commands=["new_notification"])
    if AUTHOR:
        dispatcher.register_message_handler(easter_egg_handler, commands=[AUTHOR], state="*")
