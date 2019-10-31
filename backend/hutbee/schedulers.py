# -*- coding: utf-8 -*-
"""Hutbee schedulers."""

import atexit
import pickle
import random

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from logzero import logger

from hutbee import config
from hutbee.db import DB, DB_CLIENT

try:
    import uwsgi

    UWSGI = True
except ImportError:
    UWSGI = False


class HealthcheckWorker:
    """A healthcheck worker."""

    def __init__(self):
        """Initialise the worker."""
        self.scheduler = None

    @staticmethod
    def healthcheck():
        """Do a healthcheck."""
        DB["healthchecks"].insert_one({"time": random.randint(0, 100)})
        logger.info("Healthcheck")

    def trigger_healthcheck(self):
        """Trigger a healtcheck."""
        if UWSGI:
            message = {"func": HealthcheckWorker.healthcheck, "trigger": "date"}
            uwsgi.mule_msg(pickle.dumps(message), 1)
        else:
            self.scheduler.add_job(HealthcheckWorker.healthcheck, "date")

    def run(self):
        """Start the worker."""
        self.scheduler = BackgroundScheduler()
        atexit.register(self.scheduler.shutdown)
        self.scheduler.start()

        self.scheduler.add_job(HealthcheckWorker.healthcheck, "interval", seconds=10)


class JobsWorker:
    """A job worker."""

    def __init__(self):
        """Initialise the worker."""
        self.scheduler = None

    def schedule_job(self, func, trigger, **kwargs):
        """Schedule a job."""
        if UWSGI:
            message = {"func": func, "trigger": trigger, "kwargs": kwargs}
            uwsgi.mule_msg(pickle.dumps(message), 2)
        else:
            self.scheduler.add_job(func, trigger, **kwargs)

    def run(self):
        """Start the worker."""
        self.jobstores = {
            "default": MongoDBJobStore(
                database=config.MONGO_DB_NAME,
                collection=config.JOBS_COL,
                client=DB_CLIENT,
            )
        }
        self.scheduler = BackgroundScheduler(jobstores=self.jobstores)
        atexit.register(self.scheduler.shutdown)
        self.scheduler.start()


HEALTHCHECK_WORKER = HealthcheckWorker()
JOBS_WORKER = JobsWorker()


def uwsgi_run_healtcheck_worker():
    """Run healtcheck worker from uwsgi."""
    HEALTHCHECK_WORKER.run()

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        HEALTHCHECK_WORKER.scheduler.add_job(message["func"], message["trigger"])


def uwsgi_run_job_worker():
    """Run job worker from uwsgi."""
    JOBS_WORKER.run()

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        JOBS_WORKER.scheduler.add_job(
            message["func"], message["trigger"], **message["kwargs"]
        )
