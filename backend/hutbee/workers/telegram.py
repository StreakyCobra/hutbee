#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hutbee telegram worker."""

import atexit
import os
import time
from datetime import datetime, timedelta
from functools import wraps

import kombu
import pytz
import requests
from kombu.mixins import ConsumerMixin
from logzero import logger

from hutbee import auth, config, dataprocessing
from hutbee.auth import User
from hutbee.config import DISPLAY_TIMEZONE, MEASUREMENTS_COL, USERS_COL
from hutbee.db import DB
from hutbee.models.user import User
from telegram import ChatAction, ParseMode, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    Updater,
)


def send_typing_action(func):
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)

    return command_func


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
    @send_typing_action
    def measurements(update: Update, context: CallbackContext):
        """Send the indoor measurements."""
        try:
            last = list(
                DB[MEASUREMENTS_COL].aggregate(
                    [
                        {"$sort": {"date": -1}},
                        {"$limit": 1},
                    ]
                )
            )[0]
            values = last["values"]
            timestamp = (
                datetime.fromisoformat(last["date"])
                .astimezone(DISPLAY_TIMEZONE)
                .strftime("%Y\-%m\-%d, %H:%M")
            )
            update.message.reply_text(
                f"Measurements at {timestamp}:\n"
                f"```"
                f'    Temperature: {values["temperature"]:.1f} °C\n'
                f'    Humidity:    {values["humidity"]:.0f} %\n'
                f'    CO₂:         {values["co2"]:.0f} ppm'
                f"```",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except requests.exceptions.RequestException:
            update.message.reply_text("Impossible to get the measurements")

    @staticmethod
    @send_typing_action
    def history(update: Update, context: CallbackContext):
        """Send the latest 24 hours indoor plot."""
        one_day_ago = datetime.now() - timedelta(hours=24)
        data = DB[MEASUREMENTS_COL].find({"date": {"$gte": one_day_ago.isoformat()}})
        update.message.reply_photo(dataprocessing.history_plot(data))

    @staticmethod
    @send_typing_action
    def heating_status(update: Update, context: CallbackContext):
        """Turn the heating on."""
        try:
            response = requests.get("http://controller/heating", timeout=5).json()
            update.message.reply_text(
                f"Heating status:\n"
                f"```"
                f'    Heater:  {response["heater"]}\n'
                f'    Pump:    {response["pump"]}\n'
                f"```",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except requests.exceptions.RequestException:
            update.message.reply_text("Error when trying to contact the controller")

    @staticmethod
    @send_typing_action
    def turn_heating_on(update: Update, context: CallbackContext):
        """Turn the heating on."""
        try:
            requests.post("http://controller/heating/on", timeout=5)
            update.message.reply_text(
                "The heating has been turned **ON**",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except requests.exceptions.RequestException:
            update.message.reply_text("Error when trying to contact the controller")

    @staticmethod
    @send_typing_action
    def turn_heating_off(update: Update, context: CallbackContext):
        """Turn the heating off."""
        try:
            requests.post("http://controller/heating/off", timeout=5)
            update.message.reply_text(
                "The heating has been turned **OFF**",
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        except requests.exceptions.RequestException:
            update.message.reply_text("Error when trying to contact the controller")

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

    authenticated_chat_ids = {
        user["telegramId"] for user in DB[USERS_COL].find() if "telegramId" in user
    }
    authenticated = Filters.chat(authenticated_chat_ids)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", Telegram.start))
    dp.add_handler(CommandHandler("login", Telegram.login, pass_args=True))
    dp.add_handler(CommandHandler("heating_status", Telegram.heating_status))
    dp.add_handler(CommandHandler("turn_heating_on", Telegram.turn_heating_on))
    dp.add_handler(CommandHandler("turn_heating_off", Telegram.turn_heating_off))
    dp.add_handler(
        CommandHandler(
            "measurements",
            Telegram.measurements,
            filters=authenticated,
        )
    )
    dp.add_handler(
        CommandHandler(
            "history",
            Telegram.history,
            filters=authenticated,
        )
    )
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
