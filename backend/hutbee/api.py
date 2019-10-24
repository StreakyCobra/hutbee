# -*- coding: utf-8 -*-
"""Hutbee API."""

from flask import Blueprint, escape, request

BP: Blueprint = Blueprint("api", __name__)


@BP.route("/")
def hello():
    """Hello world endpoint."""
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)}!"
