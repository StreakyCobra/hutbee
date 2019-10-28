# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
# flake8: noqa
"""Hutbee backend."""

import os

# Load `.env` file first to avoid missing env variable on import
if not os.environ.get("HUTBEE_PRODUCTION"):
    from dotenv import load_dotenv

    load_dotenv()

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from logzero import logger


from hutbee import api

# Setup Flask
APP = Flask(__name__)
APP.config["JWT_SECRET_KEY"] = os.environ['JWT_SECRET_KEY']
JWTManager(APP)
CORS(APP)


# Register blueprint
APP.register_blueprint(api.BP)
