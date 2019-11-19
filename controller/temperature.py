#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-outside-toplevel
"""Script for running hutbee controller."""

import time

from flask import Flask, jsonify

import smbus

APP = Flask(__name__)
BUS = smbus.SMBus(1)
TEMP_IN_ADDR = 0x18
TEMP_OUT_ADDR = 0x19


def read_temperature(bus, address):
    """Read the temperature in Celsius of the sensor with given address."""
    data = bus.read_i2c_block_data(address, 0x05, 2)
    temp = ((data[0] & 0x1F) * 256) + data[1]
    if temp > 4095:
        temp -= 8192
    temp = temp * 0.0625
    return temp


@APP.route("/")
def get_temperature():
    temp_in = read_temperature(BUS, TEMP_IN_ADDR)
    temp_out = read_temperature(BUS, TEMP_OUT_ADDR)
    return jsonify(temperature_inside=temp_in, temperature_outside=temp_out)


def main():
    APP.run(host="0.0.0.0", port="8700")


if __name__ == "__main__":
    main()
