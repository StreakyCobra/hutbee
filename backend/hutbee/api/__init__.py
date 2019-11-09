# -*- coding: utf-8 -*-
"""Hutbee backend."""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from hutbee import config
from hutbee.api import auth


def run(*args, **kwargs):
    """Run the API."""
    # Setup Flask
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY

    # Register Flask extensions
    JWTManager(app)
    CORS(app)

    # Register blueprints
    app.register_blueprint(auth.BP)

    # Run the API
    app.run(*args, **kwargs)
