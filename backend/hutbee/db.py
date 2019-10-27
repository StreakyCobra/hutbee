# -*- coding: utf-8 -*-
"""Hutbee database."""
import os

from pymongo import MongoClient

DB_NAME = os.environ["MONGO_DB"]

DB_CLIENT = MongoClient(
    host=os.environ["MONGO_HOST"],
    port=int(os.environ["MONGO_PORT"]),
    username=os.environ.get("MONGO_USERNAME"),
    password=os.environ.get("MONGO_PASSWORD"),
    connect=False,
    maxPoolSize=5,
)

DB = DB_CLIENT[DB_NAME]
