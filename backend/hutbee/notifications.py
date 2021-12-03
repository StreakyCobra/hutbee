# -*- coding: utf-8 -*-
"""Hutbee notifications."""

from hutbee.models.user import User
from logzero import logger


def notify_user(user: User, message):
    """Notify a message to a user."""
    if user.telegram_id:
        raise NotImplementedError("Not implemented yet")
    else:
        logger.error(f"Impossible to notify the user {user.username}")
