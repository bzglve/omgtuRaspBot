import asyncio
from datetime import datetime, timedelta

from aiogram.types import Chat, Message

from database.base import get_events, update_event
from handlers.user.handlers import event_actions
from logger import logger


async def poll(sleep_time: int | float):
    if sleep_time < 1 / 30:
        logger.warning(
            f"""Current sleep time: {sleep_time}
It can't be less than {1/30}s (30 messages per second)
dropping to {1/30}s"""
        )
        sleep_time = 1 / 30

    while True:
        events = await get_events()
        for event in events:
            if (
                event.last_update + timedelta(seconds=event.update_interval)
                < datetime.now()
                and event.enabled
            ):
                msg = Message()
                msg.chat = Chat()
                msg.chat.id = event.chat_id

                await event_actions[event.function_id]["func"](msg)

                await update_event(event.hash, last_update=datetime.now())

                break

        await asyncio.sleep(sleep_time)
