# -*- coding: utf-8 -*-
"""Hutbee jobs."""

import atexit
import pickle

from apscheduler import events
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from hutbee import config
from hutbee.db import DB_CLIENT
from logzero import logger

try:
    import uwsgi

    UWSGI = True
    MULE_NUM = 2
except ImportError:
    UWSGI = False


JOBSTORES = {
    "default": MongoDBJobStore(
        database=config.MONGO_DB_NAME, collection=config.JOBS_COL, client=DB_CLIENT
    )
}
SCHEDULER = BackgroundScheduler(jobstores=JOBSTORES)


def job_missed_listener(event):
    # TODO Notify about missed jobs
    logger.warn("A job has been missed")


def schedule_job(func, trigger, **kwargs):
    """Schedule a job."""
    if UWSGI:
        message = {"func": func, "trigger": trigger, "kwargs": kwargs}
        uwsgi.mule_msg(pickle.dumps(message), MULE_NUM)
    else:
        SCHEDULER.add_job(func, trigger, **kwargs)
    logger.info("Job scheduled")


def run_worker():
    """Start the jobs worker."""
    SCHEDULER.add_listener(job_missed_listener, events.EVENT_JOB_MISSED)
    atexit.register(SCHEDULER.shutdown)
    SCHEDULER.start()


def uwsgi_run_mule():
    """Run uwsgi mule."""
    run_worker()

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        SCHEDULER.add_job(message["func"], message["trigger"], **message["kwargs"])
