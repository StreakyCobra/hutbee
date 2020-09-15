#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script for measuring and reporting sensors values."""
import os
from datetime import datetime

import kombu
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
from scd30_i2c import SCD30

APP = Flask(__name__)
INDOOR = SCD30()
INDOOR.set_measurement_interval(2)
INDOOR.start_periodic_measurement()


def measure_indoor():
    if INDOOR.get_data_ready():
        measurement = INDOOR.read_measurement()
        return {
            "co2": measurement[0],
            "temperature": measurement[1],
            "humidity": measurement[2],
        }
    else:
        raise None


@APP.route("/")
def api_sense():
    """Return the """
    indoor = measure_indoor()
    return jsonify(indoor=indoor)


def publish_temperature(producer, exchange):
    """Publish the temperature in messaging system."""
    indoor = measure_indoor()
    producer.publish({"date": datetime.utcnow(), "indoor": indoor}, exchange=exchange)


def setup_messaging():
    user = os.environ["RABBITMQ_DEFAULT_USER"]
    password = os.environ["RABBITMQ_DEFAULT_PASS"]
    uri = f"amqp://{user}:{password}@messaging:5672"
    with kombu.Connection(
        uri, transport_options={"confirm_publish": True}
    ) as connection:
        return connection


def main():
    connection = setup_messaging()
    exchange = kombu.Exchange("measurements")(connection)
    exchange.declare()
    producer = connection.Producer()

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        publish_temperature,
        "interval",
        seconds=60,
        kwargs={"producer": producer, "exchange": exchange},
    )

    scheduler.start()
    APP.run(host="0.0.0.0", port="80")


if __name__ == "__main__":
    main()
