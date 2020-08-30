#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-outside-toplevel
"""Script for running hutbee controller."""
from datetime import datetime
import os
import kombu

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify

try:
    import smbus2

    BUS = smbus2.SMBus(1)
    FAKE = False
except FileNotFoundError:
    import random

    BUS = None
    FAKE = True

APP = Flask(__name__)
TEMP_IN_ADDR = 0x1B
TEMP_OUT_ADDR = 0x18


def read_temperature(bus, address):
    """Read the temperature in Celsius of the sensor with given address."""
    if FAKE:
        return random.random() * 20 + 10

    data = bus.read_i2c_block_data(address, 0x05, 2)
    temp = ((data[0] & 0x1F) * 256) + data[1]
    if temp > 4095:
        temp -= 8192
    temp = temp * 0.0625
    return temp


def read_temperatures():
    temp_in = read_temperature(BUS, TEMP_IN_ADDR)
    temp_out = read_temperature(BUS, TEMP_OUT_ADDR)
    return temp_in, temp_out


@APP.route("/")
def api_get_temperature():
    """Return the """
    temp_in, temp_out = read_temperatures()
    return jsonify(temperature_inside=temp_in, temperature_outside=temp_out)


def store_temperature():
    """Read and store the temperature in a file."""
    temp_in, temp_out = read_temperatures()
    date = datetime.utcnow()

    with open("/app/temperatures.csv", "a") as fd:
        fd.write(f"{date.isoformat()}, {temp_in}, {temp_out}\n")


def publish_temperature(producer, exchange):
    """Publish the temperature in messaging system."""
    producer.publish({"temperature": 0.0}, exchange=exchange)


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
    producer = connection.Producer()
    exchange = kombu.Exchange("temperatures")(connection)
    exchange.declare()

    scheduler = BackgroundScheduler()
    scheduler.add_job(store_temperature, "interval", seconds=60)
    scheduler.add_job(
        publish_temperature,
        "interval",
        seconds=1,
        kwargs={"producer": producer, "exchange": exchange},
    )

    scheduler.start()
    APP.run(host="0.0.0.0", port="80")


if __name__ == "__main__":
    main()
