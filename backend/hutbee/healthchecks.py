# -*- coding: utf-8 -*-
"""Hutbee healtchecks."""

import atexit
from datetime import datetime
import pickle

from apscheduler.schedulers.background import BackgroundScheduler
from hutbee import config
from hutbee.db import DB
from logzero import logger

try:
    import uwsgi

    UWSGI = True
except ImportError:
    UWSGI = False

SCHEDULER = BackgroundScheduler()


class HealthcheckWorker:
    """A healthcheck worker."""

    @staticmethod
    def healthcheck():
        """Do a healthcheck."""
        DB[config.HEALTHCHECKS_COL].insert_one({"time": datetime.now()})
        logger.info("Healthcheck")

    @staticmethod
    def trigger_healthcheck():
        """Trigger a healthcheck job."""
        if UWSGI:
            message = {"func": HealthcheckWorker.healthcheck, "trigger": "date"}
            uwsgi.mule_msg(pickle.dumps(message), 1)
        else:
            SCHEDULER.add_job(HealthcheckWorker.healthcheck, "date")

    @staticmethod
    def run():
        """Start the worker."""
        atexit.register(SCHEDULER.shutdown)
        SCHEDULER.start()

        SCHEDULER.add_job(HealthcheckWorker.healthcheck, "interval", seconds=10)


def uwsgi_run_worker():
    """Run worker from uwsgi."""
    HealthcheckWorker.run()

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        SCHEDULER.add_job(message["func"], message["trigger"])
