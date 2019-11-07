# -*- coding: utf-8 -*-
"""Hutbee API."""

from flask import Blueprint, request, jsonify

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
    token = auth.authenticate(data["username"], data["password"])
    if not token:
        return {"error": "Wrong credentials"}, 400
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
    return request.user.get("username")


@BP.route("/auth/register", methods=["POST"])
@authenticated
def auth_register():
    """Register a new user."""
    data = request.form
    registered = auth.register(data["username"], data["password"])
    if not registered:
        return {"error": "Can not register the user"}, 400
    return {"msg": "User successfully registered"}
