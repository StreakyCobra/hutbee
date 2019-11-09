# -*- coding: utf-8 -*-
"""Hutbee healthchecks."""

import atexit
import pickle
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from hutbee import config
from hutbee.db import DB
from logzero import logger

try:
    import uwsgi

    UWSGI = True
    MULE_NUM = 1
except ImportError:
    UWSGI = False

SCHEDULER = BackgroundScheduler()


def _healthcheck():
    """Do a healthcheck."""
    DB[config.HEALTHCHECKS_COL].insert_one({"time": datetime.now()})
    logger.info("Healthcheck")


def trigger_healthcheck():
    """Trigger a healthcheck job."""
    if UWSGI:
        message = {"func": _healthcheck, "trigger": "date"}
        uwsgi.mule_msg(pickle.dumps(message), MULE_NUM)
    else:
        SCHEDULER.add_job(_healthcheck, "date")


def run_worker():
    """Start the healthcheck worker."""
    atexit.register(SCHEDULER.shutdown)
    SCHEDULER.start()
    SCHEDULER.add_job(_healthcheck, "interval", seconds=10)


def uwsgi_run_mule():
    """Run uwsgi mule."""
    run_worker()

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        SCHEDULER.add_job(message["func"], message["trigger"])
