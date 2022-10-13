# -*- coding: utf-8 -*-
"""Hutbee notifications."""

from hutbee.config import USERS_COL
from hutbee.db import DB
from hutbee.models.user import User
from hutbee.workers.telegram import send_message
from logzero import logger


def notify_user(user: User, message):
    """Notify a user with a message."""
    if user.telegram_id:
        logger.info(f"Notifying {user.username}: {message}")
        send_message(user, message)
    else:
        logger.error(f"Impossible to notify the user {user.username}")


def notify_managers(message):
    """Notify the managers."""
    for user_json in DB[USERS_COL].find():
        user = User.of(user_json)
        if user.is_manager:
            notify_user(user, message)
