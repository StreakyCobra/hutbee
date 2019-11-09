# -*- coding: utf-8 -*-
"""Hutbee authentication API."""

from flask import Blueprint, request

from hutbee import auth
from hutbee.auth import authenticated, with_refresh_token

BP: Blueprint = Blueprint("api", __name__)


@BP.errorhandler(auth.AuthError)
def handle_invalid_usage(error):
    return "Authentication error", 403


@BP.route("/auth/login", methods=["POST"])
def auth_login():
    """Perform a user login and return the authentication token."""
    data = request.json
    user = auth.authenticate(data["username"], data["password"])
    if user is None:
        return {"error": "Wrong credentials"}, 400
    token = auth.create_token_pair(user)
    return {"access_token": token.access, "refresh_token": token.refresh}


@BP.route("/auth/refresh", methods=["POST"])
@with_refresh_token
def auth_refresh():
    """Refresh an authentication token."""
    token = auth.create_token_pair(request.user)
    return {"access_token": token.access}


@BP.route("/me")
@authenticated
def username():
    """Return username."""
    return request.user.username
