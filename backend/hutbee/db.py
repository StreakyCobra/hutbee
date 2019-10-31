# -*- coding: utf-8 -*-
"""Hutbee database."""
from pymongo import MongoClient

from hutbee import config

DB_CLIENT = MongoClient(
    host=config.MONGO_HOST,
    port=config.MONGO_PORT,
    username=config.MONGO_USERNAME,
    password=config.MONGO_PASSWORD,
    connect=False,
    maxPoolSize=5,
)

DB = DB_CLIENT[config.MONGO_DB_NAME]
