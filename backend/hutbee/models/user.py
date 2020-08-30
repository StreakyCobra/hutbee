# -*- coding: utf-8 -*-
"""Hutbee user."""
from dataclasses import dataclass
from typing import Dict, Optional

from hutbee.config import USERS_COL
from hutbee.db import DB


@dataclass
class User:
    """A user of hutbee."""

    username: str
    password: str
    telegram_id: Optional[str]

    def set_telegram_id(self, telegram_id):
        DB[USERS_COL].update_one(
            {"username": self.username}, {"$set": {"telegramId": telegram_id}}
        )
        self.telegram_id = telegram_id

    def to_document(self):
        return {
            "username": self.username,
            "password": self.password,
            "telegram_id": self.telegram_id,
        }

    @staticmethod
    def of(data: Dict):
        return User(
            username=data["username"],
            password=data["password"],
            telegram_id=data.get("telegramId"),
        )
