# -*- coding: utf-8 -*-
"""Hutbee API."""

from flask import Blueprint, request

from hutbee import auth
from hutbee.auth import authenticated

BP: Blueprint = Blueprint("api", __name__)


@BP.route("/auth/login", methods=["POST"])
def auth_login():
    """Perform a user login and return the authenticaton token."""
    data = request.form
    token = auth.authenticate(data["username"], data["password"])
    if not token:
        return {"error": "Wrong credentials"}, 400
    return {"access_token": token}


@BP.route("/auth/register", methods=["POST"])
def auth_register():
    """Register a new user."""
    data = request.form
    registered = auth.register(data["username"], data["password"])
    if not registered:
        return {"error": "Can not register the user"}, 400
    return {"msg": "User succesfully registered"}


@BP.route("/me")
@authenticated
def username():
    """Return username."""
    return request.user
