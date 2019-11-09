#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-outside-toplevel
"""Script for running hutbee backend."""

import os

from hutbee import APP
from hutbee import config


def main():
    """Entry point for running hutbee backend."""
    # Enable Visual Studio Code remote debugging in debug mode
    if config.DEBUG and "WERKZEUG_RUN_MAIN" in os.environ:
        import ptvsd

        ptvsd.enable_attach()

    # In debug mode take care of running the scheduler jobs. In production mode
    # this is managed by uwsgi.
    if config.DEBUG and "WERKZEUG_RUN_MAIN" in os.environ:
        from hutbee import healthchecks, jobs

        healthchecks.HealthcheckWorker.run()
        jobs.JobsWorker.run()

    # Run Flask
    APP.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
