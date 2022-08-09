#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
from contextlib import contextmanager
from threading import Thread

import zmq
from flask import Flask, jsonify, make_response
from pymodbus.client.sync import ModbusTcpClient

APP = Flask(__name__)
CONTEXT = zmq.Context()


class ModbusWorker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.client = ModbusTcpClient(os.environ["MODBUS_SERVER_HOST"])
        self.socket = CONTEXT.socket(zmq.REP)

    def run(self):
        self.socket.bind("inproc://stream")
        while True:
            args = self.socket.recv_json()
            result = self.execute(args)
            self.socket.send_json(result)

    def execute(self, args):
        command = args.get("command")
        if command == "set_watchdog":
            return self.set_watchdog(args["value"])
        elif command == "heating_status":
            return self.heating_status()
        elif command == "turn_heating_on":
            return self.turn_heating_on()
        elif command == "turn_heating_off":
            return self.turn_heating_off()
        else:
            return {"content": {"message": "Unknown command"}, "status": 400}

    def set_watchdog(self, value):
        try:
            self.client.write_coil(0, int(value))
            return {"content": {"message": "The watchdog has been set"}, "status": 200}
        except:
            return {
                "content": {"message": "Can not set the watchdog"},
                "status": 400,
            }

    def heating_status(self):
        try:
            coils = self.client.read_coils(80, 8).bits
            heater = "ON" if coils[1] else "OFF"
            pump = "ON" if coils[2] else "OFF"
            return {"content": {"heater": heater, "pump": pump}, "status": 200}
        except:
            return {
                "content": {"message": "Can not access the heating status"},
                "status": 400,
            }

    def turn_heating_on(self):
        try:
            self.client.write_coil(1, 1)
            return {
                "content": {"message": "The heating has been turned on"},
                "status": 200,
            }
        except:
            return {
                "content": {"message": "Can not turn the heating on"},
                "status": 400,
            }

    def turn_heating_off(self):
        try:
            self.client.write_coil(1, 0)
            return {
                "content": {"message": "The heating has been turned off"},
                "status": 200,
            }
        except:
            return {
                "content": {"message": "Can not turn the heating off"},
                "status": 400,
            }


@contextmanager
def channel():
    socket = CONTEXT.socket(zmq.REQ)
    socket.connect("inproc://stream")
    try:
        yield socket
    finally:
        socket.close()


@APP.route("/healthcheck", methods=["GET"])
def healtcheck():
    """Healthcheck endpoint."""
    return jsonify({"state": "good"})


@APP.route("/heating", methods=["GET"])
def heating_status():
    """Get the heating status."""
    with channel() as socket:
        socket.send_json({"command": "heating_status"})
        response = socket.recv_json()
        return make_response(response["content"], response["status"])


@APP.route("/heating/on", methods=["POST"])
def turn_heating_on():
    """Turn the heating on."""
    with channel() as socket:
        socket.send_json({"command": "turn_heating_on"})
        response = socket.recv_json()
        return make_response(response["content"], response["status"])


@APP.route("/heating/off", methods=["POST"])
def turn_heating_off():
    """Turn the heating off."""
    with channel() as socket:
        socket.send_json({"command": "turn_heating_off"})
        response = socket.recv_json()
        return make_response(response["content"], response["status"])


def watchdog():
    state = True
    with channel() as socket:
        while True:
            state = not state
            socket.send_json({"command": "set_watchdog", "value": state})
            socket.recv_json()
            time.sleep(1)


def main():
    worker = ModbusWorker()
    worker.start()

    thread = Thread(target=watchdog)
    thread.daemon = True
    thread.start()

    APP.run(host="0.0.0.0", port="80")


if __name__ == "__main__":
    main()
