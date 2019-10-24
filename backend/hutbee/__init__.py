# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position
# flake8: noqa
"""Hutbee backend."""

import os
from pathlib import Path

from flask import Flask

from flask_cors import CORS
from hutbee import api

# Load `.env` file first to avoid missing env variable on import
if not os.environ.get("HUTBEE_PRODUCTION"):
    from dotenv import load_dotenv

    load_dotenv()


# Setup Flask
APP = Flask(__name__)
CORS(APP)

# Register blueprint
APP.register_blueprint(api.BP)
