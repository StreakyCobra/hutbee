# -*- coding: utf-8 -*-
# pylint: skip-file
# flake8: noqa
"""Hutbee backend."""

from hutbee import config  # Imported first to avoid missing env. variables

import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from hutbee import api

# Setup Flask
APP = Flask(__name__)
APP.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
JWTManager(APP)
CORS(APP)

# Register blueprint
APP.register_blueprint(api.BP)
