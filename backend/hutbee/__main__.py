#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script for running hutbee backend."""

import os

import ptvsd

from hutbee import APP


def main():
    """Entry point for running hutbee backend."""

    # Debug is enabled by default except in production mode
    debug = not os.environ.get("HUTBEE_PRODUCTION", False)

    if debug:
        # Workaround for the werkzeug reloader removing the current directory
        # from the path. It's nasty, but it works! Inspired by:
        # https://github.com/mitsuhiko/flask/issues/1246
        os.environ["PYTHONPATH"] = os.getcwd()

        # Enable Visual Studio Code remote debugging when in debug mode
        if "WERKZEUG_RUN_MAIN" in os.environ:
            ptvsd.enable_attach()

    # Run Flask
    APP.run(host="0.0.0.0", port=8000, debug=debug)


if __name__ == "__main__":
    main()
