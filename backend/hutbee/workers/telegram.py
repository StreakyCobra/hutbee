# -*- coding: utf-8 -*-
"""Hutbee telegram worker."""

import atexit
import pickle
from dataclasses import dataclass

from hutbee import config, auth
from hutbee.auth import User
from logzero import logger
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

try:
    import uwsgi

    UWSGI = True
    MULE_NUM = 3
except ImportError:
    UWSGI = False

UPDATER = Updater(config.TELEGRAM_BOT_TOKEN, use_context=True)


@dataclass
class _Message:
    user: User
    text: str


class _Telegram:
    @staticmethod
    def start(update, context):
        """Send a message when the command /start is issued."""
        update.message.reply_text("Welcome to hutbee")
        update.message.reply_text(
            "Please start by login in, using the command:"
            "\n\n/login username password"
        )

    @staticmethod
    def login(update: Update, context: CallbackContext):
        """Send a message when the command /help is issued."""
        if not context.args or len(context.args) != 2:
            update.message.reply_text(
                "You should specify your username and password as argument:"
                "\n\n/login username password"
            )
            return

        username = context.args[0]
        password = context.args[1]
        user = auth.authenticate(username, password)

        if not user:
            update.message.reply_text("Wrong credentials")
            return

        user.set_telegram_id(update.effective_user.id)

        update.message.reply_text(
            f"Welcome, {user.username}. You have been authenticated"
        )

    @staticmethod
    def echo(update, context):
        """Echo the user message."""
        update.message.reply_text(update.message.text)

    @staticmethod
    def error(update, context):
        """Log Errors caused by Updates."""
        logger.error('Telegram: update "%s" caused error "%s"', update, context.error)


def _send_message(message: _Message):
    """Send a message to the user."""
    UPDATER.bot.send_message(chat_id=message.user.telegram_id, text=message.text)


def send_message(user: User, message: str):
    """Send a message to the user."""
    message = _Message(user=user, text=message)
    if UWSGI:
        uwsgi.mule_msg(pickle.dumps(message), MULE_NUM)
    else:
        _send_message(message)


def run_worker(is_mule=True):
    """Run telegram worker."""
    atexit.register(UPDATER.stop)

    dp = UPDATER.dispatcher
    dp.add_handler(CommandHandler("start", _Telegram.start))
    dp.add_handler(CommandHandler("login", _Telegram.login, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text, _Telegram.echo))
    dp.add_error_handler(_Telegram.error)

    UPDATER.start_polling()

    if not is_mule:
        return

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        _send_message(message)
