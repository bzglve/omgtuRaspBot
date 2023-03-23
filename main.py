#!.venv/bin/python
from aiogram import executor as ex

import handlers  # noqa: F401
from loader import dp
from util.commands import set_default_commands


async def on_startup(dp):
    await set_default_commands(dp)


async def on_shutdown(dp):
    pass


def main():
    ex.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)


if __name__ == "__main__":
    main()
