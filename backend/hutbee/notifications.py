# -*- coding: utf-8 -*-
"""Hutbee notifications."""

from hutbee.models.user import User
from hutbee.mules import telegram
from logzero import logger


def notify_user(user: User, message):
    """Notify a message to a user."""
    if user.telegram_id:
        telegram.send_message(user, message)
    else:
        logger.error(f"Impossible to notify the user {user.username}")
