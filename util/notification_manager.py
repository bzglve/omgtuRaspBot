import asyncio
from time import time

from aiogram.types import Chat, Message

from database.base import add_event, get_events, remove_event
from handlers.user.handlers import event_actions
from logger import logger


async def poll(sleep_for: int | float):
    if sleep_for < 1 / 30:
        logger.warning(
            f"""Current sleep time: {sleep_for}
It can't be less than {1/30}s (30 messages per second)
dropping to {1/30}s"""
        )
        sleep_time = 1 / 30

    while True:
        # print(f"POLLING {time()}")

        events = get_events()
        for event in events:
            if event["last_update"] + event["interval"] < time() and event["enabled"]:
                msg = Message()
                msg.chat = Chat()
                msg.chat.id = event["chat_id"]

                await event_actions[event["function"]]["func"](msg)

                # TODO update event instead of removing and adding new
                remove_event(event)
                event["last_update"] = int(time())
                add_event(event)

                break

        await asyncio.sleep(sleep_time)


def setup(chat_id: int, start_time: int, interval: int, action_id: int):
    event = {
        "id": hash(chat_id + action_id),
        "interval": interval,  # time in seconds
        "last_update": int(time()),  # last update
        "chad_id": chat_id,
        "function": action_id,  # function index
        "args": [],
        "kwargs": {},
        "enabled": True,
    }
    events = get_events()
    for event_t in events:
        if event_t["id"] == event["id"]:
            break
    else:
        add_event(event)


def delete():
    pass
