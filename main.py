#!.venv/bin/python
from aiogram import executor as ex

from loader import dp
from util.commands import register_handlers, set_default_commands


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)
    register_handlers(dispatcher)


async def on_shutdown(dispatcher):
    pass


def main():
    ex.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == "__main__":
    main()
