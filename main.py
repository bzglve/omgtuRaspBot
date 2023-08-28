#!.venv/bin/python
from aiogram import Dispatcher
from aiogram import executor as ex

from config.config import poll_interval
from loader import dp, loop
from util.commands import register_handlers, set_default_commands
from util.notification_manager import poll


async def on_startup(dispatcher: Dispatcher):
    await set_default_commands(dispatcher)
    register_handlers(dispatcher)


async def on_shutdown(dispatcher):
    pass


def main():
    loop.create_task(poll(sleep_time=poll_interval))
    ex.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == "__main__":
    main()
