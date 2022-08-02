#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script for measuring and reporting sensors values."""
import os

from flask import Flask, jsonify, make_response
from pymodbus.client.sync import ModbusTcpClient

APP = Flask(__name__)

client = ModbusTcpClient(os.environ["MODBUS_SERVER_HOST"])


@APP.route("/heating", methods=["GET"])
def heating_status():
    """Turn the heating on."""
    try:
        coils = client.read_coils(80, 8).bits
        heater = "ON" if coils[1] else "OFF"
        pump = "ON" if coils[2] else "OFF"
        return jsonify(heater=heater, pump=pump)
    except:
        return make_response(jsonify(message="Can not access the heating status"), 400)


@APP.route("/heating/on", methods=["POST"])
def turn_heating_on():
    """Turn the heating on."""
    try:
        coils = client.write_coil(1, 1)
        return jsonify(message="The heating has been turned ON.")
    except:
        return make_response(jsonify(message="Can not turn ON the heating"), 400)


@APP.route("/heating/off", methods=["POST"])
def turn_heating_off():
    """Turn the heating off."""
    try:
        coils = client.write_coil(1, 0)
        return jsonify(message="The heating has been turned OFF.")
    except:
        return make_response(jsonify(message="Can not turn OFF the heating"), 400)


def main():
    APP.run(host="0.0.0.0", port="80")


if __name__ == "__main__":
    main()
