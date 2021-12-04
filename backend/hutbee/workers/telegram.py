#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hutbee telegram worker."""

import atexit
import os
import time

import kombu
from kombu.mixins import ConsumerMixin
from logzero import logger

from hutbee import auth, config
from hutbee.auth import User
from hutbee.config import USERS_COL
from hutbee.db import DB
from hutbee.models.user import User
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)


class Telegram:
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


class Worker(ConsumerMixin):
    def __init__(self, connection, queue, updater):
        self.connection = connection
        self.queue = queue
        self.updater = updater

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(
                queues=self.queue,
                callbacks=[self.notify],
            )
        ]

    def notify(self, body, message):
        """Notify a user."""
        db_user = DB[USERS_COL].find_one({"username": body["username"]})
        user = User.of(db_user)
        self.updater.bot.send_message(
            chat_id=user.telegram_id,
            text=str(body["message"]),
        )
        message.ack()


def main():
    """Run telegram worker."""
    updater = Updater(config.TELEGRAM_BOT_TOKEN, use_context=True)
    atexit.register(updater.stop)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", Telegram.start))
    dp.add_handler(CommandHandler("login", Telegram.login, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text, Telegram.echo))
    dp.add_error_handler(Telegram.error)

    updater.start_polling()
    user = os.environ["BACKEND_RABBITMQ_USERNAME"]
    password = os.environ["BACKEND_RABBITMQ_PASSWORD"]
    uri = f"amqp://{user}:{password}@backend-rabbitmq:5672"
    queue = kombu.Queue("notifications.telegram")

    while True:
        try:
            with kombu.Connection(uri) as connection:
                with connection.channel() as channel:
                    queue.declare(channel=channel)
                worker = Worker(connection, queue, updater)
                worker.run()
        except ConnectionError:
            logger.warning("Connection to rabbitmq failed")
        time.sleep(60)


if __name__ == "__main__":
    main()
