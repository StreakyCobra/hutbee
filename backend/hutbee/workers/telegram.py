# -*- coding: utf-8 -*-
"""Hutbee telegram worker."""

import atexit
import pickle
from dataclasses import dataclass

from hutbee import config
from hutbee.auth import User
from logzero import logger
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

try:
    import uwsgi

    UWSGI = True
    MULE_NUM = 3
except ImportError:
    UWSGI = False

UPDATER = Updater(config.TELEGRAM_BOT_TOKEN, use_context=True)


@dataclass
class _Message:
    to: User
    message: str


class _Telegram:
    @staticmethod
    def start(update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text("Bienvenue sur hutbee.")
        update.message.reply_text(
            "Afin de pouvoir utiliser hutsbee, tu dois te connecter en tapant /login"
        )

    @staticmethod
    def login(update, context):
        """Send a message when the command /help is issued."""
        update.message.reply_text("Help!")

    @staticmethod
    def echo(update, context):
        """Echo the user message."""
        update.message.reply_text(update.message.text)

    @staticmethod
    def error(update, context):
        """Log Errors caused by Updates."""
        logger.error('Telegram: update "%s" caused error "%s"', update, context.error)


def _send_message(_Message):
    """Send a message to the user."""
    # TODO send message
    pass


def send_message(user: User, message: str):
    """Send a message to the user."""
    message = _Message(to=user, message=message)
    if UWSGI:
        uwsgi.mule_msg(pickle.dumps(message), MULE_NUM)
    else:
        _send_message(message)


def run_worker(is_mule=True):
    """Run telegram worker."""
    atexit.register(UPDATER.stop)

    dp = UPDATER.dispatcher
    dp.add_handler(CommandHandler("start", _Telegram.start))
    dp.add_handler(CommandHandler("login", _Telegram.login))
    dp.add_handler(MessageHandler(Filters.text, _Telegram.echo))
    dp.add_error_handler(_Telegram.error)

    UPDATER.start_polling()

    if not is_mule:
        return

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        _send_message(message)
