#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script for running hutbee backend."""

import os

from hutbee import APP


def main():
    """Entry point for running hutbee backend."""
    # Debug mode is enabled by default except in production mode
    debug = not os.environ.get("HUTBEE_PRODUCTION", False)

    # Enable Visual Studio Code remote debugging in debug mode
    if debug and "WERKZEUG_RUN_MAIN" in os.environ:
        import ptvsd

        ptvsd.enable_attach()

    # In debug mode take care of running the scheduler jobs. In production mode
    # this is managed by uwsgi.
    if debug and "WERKZEUG_RUN_MAIN" in os.environ:
        from hutbee import schedulers

        schedulers.healthcheck_worker(uwsgi_mule=False)
        schedulers.jobs_worker(uwsgi_mule=False)

    # Run Flask
    APP.run(host="0.0.0.0", port=8000, debug=debug)


if __name__ == "__main__":
    main()
