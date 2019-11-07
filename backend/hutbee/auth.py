# -*- coding: utf-8 -*-
"""Hutbee authentication."""
import collections
from typing import Optional, Dict

import bcrypt
import flask_jwt_extended as jwt
from decorator import decorator
from flask import request
from hutbee.config import USERS_COL
from hutbee.db import DB
from logzero import logger
from pymongo.errors import DuplicateKeyError


class AuthError(Exception):
    """An authentication error occurred."""

    ...


TokenPair = collections.namedtuple("TokenPair", ["access", "refresh"])
"""A pair of access and refresh token."""


def authenticate(username: str, password: str) -> Optional[TokenPair]:
    """Authenticate a user.

    If the authentication succeeded, return an authentication token and a
    refresh token. If the authentication failed return None.
    """
    user = DB[USERS_COL].find_one({"username": username})
    if not user:
        logger.warn(f"Unknown user: {username}")
        return None
    if not bcrypt.checkpw(password.encode(), user["password"]):
        logger.warn(f"Wrong password for user: {username} ")
        return None
    logger.info(f"Authentication successful for user: {username}")
    return create_token_pair(user)


def create_token_pair(user: Dict) -> TokenPair:
    """Create a pair of access and refresh token for a given user."""
    return TokenPair(
        access=jwt.create_access_token(identity=user["username"]),
        refresh=jwt.create_refresh_token(identity=user["username"]),
    )


def register(username: str, password: str) -> bool:
    """Register a new user."""
    password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        DB[USERS_COL].insert_one({"username": username, "password": password})
    except DuplicateKeyError:
        return False
    return True


def validate_user() -> Dict:
    """Get username from JWT token and return corresponding user from database."""
    username = jwt.get_jwt_identity()
    user = DB[USERS_COL].find_one({"username": username})
    if not user:
        raise AuthError
    return user


@decorator
@jwt.jwt_required
def authenticated(f, *args, **kwargs):
    """Ensure a user is authenticated."""
    request.user = validate_user()
    return f(*args, **kwargs)


@decorator
@jwt.jwt_refresh_token_required
def with_refresh_token(f, *args, **kwargs):
    """Ensure a refresh token is present and the user still exists."""
    request.user = validate_user()
    return f(*args, **kwargs)
