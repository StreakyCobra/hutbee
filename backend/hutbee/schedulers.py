# -*- coding: utf-8 -*-
# pylint: disable=global-statement
"""Hutbee schedulers."""

import atexit
import pickle
import random

from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from logzero import logger

from hutbee.db import DB, DB_CLIENT, DB_NAME

try:
    import uwsgi
except ImportError:
    pass

HEALTHCHECK_WORKER = None
JOBS_WORKER = None


def healthcheck():
    """Do a healthcheck."""
    DB["healthchecks"].insert_one({"time": random.randint(0, 100)})
    logger.info("Healthcheck")


def healthcheck_worker(uwsgi_mule=True):
    """Run the healthchecks worker."""
    sched = BackgroundScheduler()
    atexit.register(sched.shutdown)
    sched.start()

    sched.add_job(healthcheck, "interval", seconds=10)

    if not uwsgi_mule:
        global HEALTHCHECK_WORKER
        HEALTHCHECK_WORKER = sched
        return

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        sched.add_job(message["func"], message["trigger"])


def jobs_worker(uwsgi_mule=True):
    """Run the jobs scheduler."""
    jobstores = {
        "default": MongoDBJobStore(
            database=DB_NAME, collection="jobs", client=DB_CLIENT
        )
    }
    sched = BackgroundScheduler(jobstores=jobstores)
    atexit.register(sched.shutdown)
    sched.start()

    if not uwsgi_mule:
        global JOBS_WORKER
        JOBS_WORKER = sched
        return

    while True:
        message = pickle.loads(uwsgi.mule_get_msg())
        sched.add_job(message["func"], message["trigger"], **message["kwargs"])


def trigger_healthcheck():
    """Trigger a healtcheck."""
    if HEALTHCHECK_WORKER is not None:
        HEALTHCHECK_WORKER.add_job(healthcheck, "date")
    else:
        message = {"func": healthcheck, "trigger": "date"}
        uwsgi.mule_msg(pickle.dumps(message), 1)


def schedule_job(func, trigger, **kwargs):
    """Schedule a job."""
    if JOBS_WORKER is not None:
        JOBS_WORKER.add_job(func, trigger, **kwargs)
    else:
        message = {"func": func, "trigger": trigger, "kwargs": kwargs}
        uwsgi.mule_msg(pickle.dumps(message), 2)
