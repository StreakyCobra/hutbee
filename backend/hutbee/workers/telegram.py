#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hutbee telegram worker."""

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


class _Telegram:
    @staticmethod
    def start(update: Update, context: CallbackContext):
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
    def echo(update: Update, context: CallbackContext):
        """Echo the user message."""
        update.message.reply_text(update.message.text)

    @staticmethod
    def error(update: Update, context: CallbackContext):
        """Log Errors caused by Updates."""
        logger.error('Telegram: update "%s" caused error "%s"', update, context.error)


def main():
    """Run telegram worker."""
    updater = Updater(config.TELEGRAM_BOT_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", _Telegram.start))
    dp.add_handler(CommandHandler("login", _Telegram.login, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text, _Telegram.echo))
    dp.add_error_handler(_Telegram.error)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
