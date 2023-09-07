from aiogram import Dispatcher

from handlers.default.handlers import start_handler, cancel_handler


def setup(dispatcher: Dispatcher):
    dispatcher.register_message_handler(cancel_handler, commands=["cancel"], state="*")
    dispatcher.register_message_handler(start_handler, commands=["start"])
