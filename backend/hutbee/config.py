# -*- coding: utf-8 -*-
"""Hutbee configuration."""

import os

from dotenv import load_dotenv

# Load `.env` file first
load_dotenv()


# Define helper functions
def int_of(value: str) -> int:
    """Return the value as an integer."""
    return int(value) if value else None


def bool_of(value: str) -> bool:
    """Return the value as a boolean."""
    if isinstance(value, bool):
        return value
    return value.lower() in ["1", "true"]


# --------------------------------------------------------------------------- #
# BACKEND CONFIGURATION                                                       #
# --------------------------------------------------------------------------- #

HOST = os.environ.get("HUTBEE_HOST", "0.0.0.0")
"""The host hutbee backend should listen to."""

PORT = int_of(os.environ.get("HUTBEE_PORT", "8000"))
"""The port hutbee backend should listen to."""

PRODUCTION = bool_of(os.environ.get("HUTBEE_PRODUCTION", False))
"""Whether the production mode is enabled."""

DEBUG = bool_of(os.environ.get("HUTBEE_DEBUG", not PRODUCTION))
"""Whether the debug mode is enabled."""

CONTROLLER_HOSTNAME = os.environ["CONTROLLER_HOSTNAME"]
"""The hostname to access the controller API."""

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
"""Secret key to sign JWTs."""

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
"""Token of the telegram bot."""


# --------------------------------------------------------------------------- #
# MONGO CONNECTION                                                            #
# --------------------------------------------------------------------------- #

MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]
"""Name of the mongodb database."""

MONGO_HOST = os.environ.get("MONGO_HOST", None)
"""Hostname to connect to the mongodb instance."""

MONGO_PORT = int_of(os.environ.get("MONGO_PORT", None))
"""Port to connect to the mongodb instance."""

MONGO_USERNAME = os.environ.get("MONGO_USERNAME", None)
"""Username to connect to the mongdb instance."""

MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", None)
"""Password to connect to the mongdb instance."""


# --------------------------------------------------------------------------- #
# MONGO COLLECTIONS                                                           #
# --------------------------------------------------------------------------- #

USERS_COL = "users"
"""Name of the users collection in the database."""

JOBS_COL = "jobs"
"""Name of the jobs collection in the database."""

HEALTHCHECKS_COL = "healthchecks"
"""Name of the healthchecks collection in the database."""

MEASUREMENTS_COL = "measurements"
"""Name of the measurements collection in the database."""
