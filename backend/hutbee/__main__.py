#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-outside-toplevel
"""Script for running hutbee backend."""

import os

from hutbee import config
from hutbee.api import APP


def main():
    """Entry point for running hutbee backend."""
    # Enable Visual Studio Code remote debugging in debug mode
    if config.DEBUG and "WERKZEUG_RUN_MAIN" in os.environ:
        import ptvsd

        ptvsd.enable_attach()

    # In debug mode take care of running the scheduler jobs. In production mode
    # this is managed with uwsgi mules.
    if config.DEBUG and "WERKZEUG_RUN_MAIN" in os.environ:
        from hutbee import healthchecks, jobs, telegram

        healthchecks.run_worker()
        jobs.run_worker()
        telegram.run_worker()

    # Run Flask
    APP.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)


if __name__ == "__main__":
    main()
