# -*- coding: utf-8 -*-
"""Hutbee jobs."""

import atexit
import pickle

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from logzero import logger

from hutbee import config
from hutbee.db import DB_CLIENT

try:
    import uwsgi

    UWSGI = True
except ImportError:
    UWSGI = False

JOBSTORES = {
    "default": MongoDBJobStore(
        database=config.MONGO_DB_NAME, collection=config.JOBS_COL, client=DB_CLIENT
    )
}
SCHEDULER = BackgroundScheduler(jobstores=JOBSTORES)


class JobsWorker:
    """A job worker."""

    @staticmethod
    def schedule_job(self, func, trigger, **kwargs):
        """Schedule a job."""
        if UWSGI:
            message = {"func": func, "trigger": trigger, "kwargs": kwargs}
            uwsgi.mule_msg(pickle.dumps(message), 2)
        else:
            SCHEDULER.add_job(func, trigger, **kwargs)
        logger.info("Job scheduled")

    @staticmethod
    def run():
        """Start the worker."""
        atexit.register(SCHEDULER.shutdown)
        SCHEDULER.start()


def uwsgi_run_worker():
    """Run worker from uwsgi."""
    JobsWorker.run()

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        SCHEDULER.add_job(message["func"], message["trigger"], **message["kwargs"])
