# -*- coding: utf-8 -*-
"""Hutbee authentication."""

from typing import Optional

import bcrypt
import pymongo
from pymongo.errors import DuplicateKeyError
from decorator import decorator
from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from hutbee.config import USERS_COL
from hutbee.db import DB


def authenticate(username: str, password: str) -> Optional[str]:
    """Authenticate a user."""
    user = DB[USERS_COL].find_one({"username": username})
    if not user:
        return None
    if not bcrypt.checkpw(password.encode(), user["password"]):
        return None
    return create_access_token(username)


def register(username: str, password: str) -> bool:
    """Register a new user."""
    password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        DB[USERS_COL].insert_one({"username": username, "password": password})
    except DuplicateKeyError:
        return False
    return True


@decorator
@jwt_required
def authenticated(f, *args, **kwargs):
    """Ensure a user is authenticated."""
    user = get_jwt_identity()
    # TODO Check for user status
    request.user = user
    return f(*args, **kwargs)
