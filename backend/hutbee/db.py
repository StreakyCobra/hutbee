# -*- coding: utf-8 -*-
"""Hutbee database."""
import os

from pymongo import MongoClient
from hutbee import config

# Helper function
def int_of(value):
    """Return the value as an integer if not None."""
    return int(value) if value else None


DB_NAME = config.MONGO_DB_NAME

DB_CLIENT = MongoClient(
    host=config.MONGO_HOST,
    port=int_of(config.MONGO_PORT),
    username=config.MONGO_USERNAME,
    password=config.MONGO_PASSWORD,
    connect=False,
    maxPoolSize=5,
)

DB = DB_CLIENT[DB_NAME]
