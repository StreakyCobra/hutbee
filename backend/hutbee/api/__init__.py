# -*- coding: utf-8 -*-
"""Hutbee API."""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from hutbee import config
from hutbee.api import auth

# Setup Flask
APP = Flask(__name__)
APP.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY

# Register Flask extensions
JWTManager(APP)
CORS(APP)

# Register blueprints
APP.register_blueprint(auth.BP)
