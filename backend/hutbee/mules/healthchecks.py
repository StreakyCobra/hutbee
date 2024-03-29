# -*- coding: utf-8 -*-
"""Hutbee healthchecks worker."""

import atexit
import pickle
from datetime import datetime
from typing import Any

import requests

from apscheduler.schedulers.background import BackgroundScheduler
from hutbee import config
from hutbee.db import DB
from hutbee.notifications import notify_managers
from logzero import logger

try:
    import uwsgi

    UWSGI = True
    MULE_NUM = 1
except ImportError:
    UWSGI = False

_SCHEDULER = BackgroundScheduler()
_LAST_STATUS = None


class _Message:
    function: Any
    trigger: str


def _healthcheck():
    """Do a healthcheck."""
    try:
        response = requests.get("http://controller/healthcheck", timeout=5)
    except:
        response = None

    if response and response.status_code == 200:
        status = "online"
    else:
        status = "offline"

    global _LAST_STATUS
    if _LAST_STATUS is not None and status != _LAST_STATUS:
        # Healthcheck status changed, notifying managers
        notify_managers(f"Status changed: {status}")
    _LAST_STATUS = status

    DB[config.HEALTHCHECKS_COL].insert_one({"time": datetime.now(), "status": status})
    logger.info(f"Healthcheck, status={status}")


def _trigger_healthcheck(message: _Message):
    """Trigger a healthcheck job message."""
    _SCHEDULER.add_job(message.function, message.trigger)


def trigger_healthcheck():
    """Trigger a healthcheck job."""
    message = _Message(function=_healthcheck, trigger="date")
    if UWSGI:
        uwsgi.mule_msg(pickle.dumps(message), MULE_NUM)
    else:
        _trigger_healthcheck(message)


def run_worker(is_mule=True):
    """Run the healthcheck worker."""
    atexit.register(_SCHEDULER.shutdown)
    _SCHEDULER.add_job(_healthcheck, "interval", seconds=60)
    _SCHEDULER.start()

    if not is_mule:
        return

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        _trigger_healthcheck(message)
