# -*- coding: utf-8 -*-
"""Hutbee configuration."""

import os

from dotenv import load_dotenv

# Load `.env` file first
load_dotenv()


# --------------------------------------------------------------------------- #
# Hutbee parameters                                                           #
# --------------------------------------------------------------------------- #

PRODUCTION = os.environ.get("HUTBEE_PRODUCTION", False)
"""Whether the production mode is enabled."""

DEBUG = os.environ.get("HUTBEE_DEBUG", not PRODUCTION)
"""Whether the debug mode is enabled."""


# --------------------------------------------------------------------------- #
# MONGO CONNECTION                                                            #
# --------------------------------------------------------------------------- #

MONGO_DB_NAME = os.environ["MONGO_DB_NAME"]
"""Name of the mongodb database."""

MONGO_HOST = os.environ.get("MONGO_HOST", None)
"""Hostname to connect to the mongodb instance."""

MONGO_PORT = os.environ.get("MONGO_PORT", None)
"""Port to connect to the mongodb instance."""

MONGO_USERNAME = os.environ.get("MONGO_USERNAME", None)
"""Username to connect to the mongdb instance."""

MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD", None)
"""Password to connect to the mongdb instance."""


# --------------------------------------------------------------------------- #
# MONGO COLLECTION                                                            #
# --------------------------------------------------------------------------- #

USERS_COL = "users"
"""Name of th users collection in the database."""


# --------------------------------------------------------------------------- #
# AUTHENTICATION                                                              #
# --------------------------------------------------------------------------- #

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
"""Secret key to sign JWTs."""
