# -*- coding: utf-8 -*-
"""Hutbee telegram."""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from logzero import logger

import atexit
import pickle

from hutbee import config
from logzero import logger

try:
    import uwsgi

    UWSGI = True
    MULE_NUM = 3
except ImportError:
    UWSGI = False

UPDATER = Updater(config.TELEGRAM_BOT_TOKEN, use_context=True)


def send_message(user, message):
    """Send a message to the user."""
    if UWSGI:
        message = {"username": user.username, "message": message}
        uwsgi.mule_msg(pickle.dumps(message), MULE_NUM)
    else:
        # TODO send message
        pass
    logger.info("Telegram message sent")


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def run_worker():
    """Start the bot."""
    atexit.register(Updater.stop)
    dp = UPDATER.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    UPDATER.start_polling()


def uwsgi_run_mule():
    """Run uwsgi mule."""
    run_worker()

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        # TODO
