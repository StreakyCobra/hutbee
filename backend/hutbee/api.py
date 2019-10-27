# -*- coding: utf-8 -*-
"""Hutbee API."""

from datetime import datetime, timedelta

from flask import Blueprint, escape, jsonify, request

from hutbee import schedulers
from hutbee.db import DB

BP: Blueprint = Blueprint("api", __name__)


def do_job():
    print("JOB DONE!")


@BP.route("/")
def hello():
    """Hello world endpoint."""
    name = request.args.get("name", "World")
    return f"Hello, {escape(name)}!"


@BP.route("/healthchecks")
def list_healthchecks():
    """List healthchecks in DB."""
    job = DB["healthchecks"].find({})
    return jsonify([j["time"] for j in job])


@BP.route("/healthchecks/add")
def add_healthchecks():
    """Add a healthcheck."""
    schedulers.trigger_healthcheck()
    return "New healthcheck triggered"


@BP.route("/jobs/add")
def add_job():
    """Add a job."""
    later = datetime.now() + timedelta(seconds=10)
    schedulers.schedule_job(do_job, "date", run_date=later)
    return "Job will run at " + str(later)


@BP.route("/jobs")
def list_jobs():
    """List jobs stored in DB."""
    jobs = list(DB["jobs"].find({}))
    return str(len(jobs))
