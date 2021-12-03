#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-outside-toplevel
"""Script for running hutbee backend."""

import os

from hutbee import config
from hutbee.api import APP


def main():
    """Entry point for running hutbee backend."""
    # In debug mode take care of running the scheduler jobs. In production mode
    # this is managed with uwsgi mules.
    if config.DEBUG and "WERKZEUG_RUN_MAIN" in os.environ:
        from hutbee.workers import feeder
        from hutbee.mules import healthchecks
        from hutbee.mules import jobs

        feeder.run_worker()
        healthchecks.run_worker(is_mule=False)
        jobs.run_worker(is_mule=False)

    # Run Flask
    APP.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
