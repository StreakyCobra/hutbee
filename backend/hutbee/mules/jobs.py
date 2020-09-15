# -*- coding: utf-8 -*-
"""Hutbee jobs worker."""

import atexit
import pickle
from dataclasses import dataclass
from typing import Callable, Any, Union

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


_JOBSTORES = {
    "default": MongoDBJobStore(
        database=config.MONGO_DB_NAME, collection=config.JOBS_COL, client=DB_CLIENT
    )
}
_SCHEDULER = BackgroundScheduler(jobstores=_JOBSTORES)


@dataclass
class _Message:
    function: Any
    trigger: str
    kwargs: dict


def _job_missed_listener(event):
    # TODO Log an notify about missed jobs
    logger.warn("A job has been missed")


def _schedule_job(message: _Message):
    """Schedule a job from a message."""
    _SCHEDULER.add_job(message.function, message.trigger, **message.kwargs)


def schedule_job(func, trigger, **kwargs):
    """Schedule a job."""
    message = _Message(function=func, trigger=trigger, kwargs=kwargs)
    if UWSGI:
        uwsgi.mule_msg(pickle.dumps(message), MULE_NUM)
    else:
        _schedule_job(message)


def run_worker(is_mule=True):
    """Run the jobs worker."""
    atexit.register(_SCHEDULER.shutdown)
    _SCHEDULER.add_listener(_job_missed_listener, events.EVENT_JOB_MISSED)
    _SCHEDULER.start()

    if not is_mule:
        return

    while True:
        message: _Message = pickle.loads(uwsgi.mule_get_msg())
        _schedule_job(message)
