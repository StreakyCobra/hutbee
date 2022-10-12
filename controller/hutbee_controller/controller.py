#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from contextlib import contextmanager

import zmq
from flask import Blueprint, jsonify, make_response

from hutbee_controller.config import ZMQ_CONTEXT

BP = Blueprint("hutbee_controller", __name__)


@contextmanager
def channel():
    socket = ZMQ_CONTEXT.socket(zmq.REQ)
    socket.connect("inproc://stream")
    try:
        yield socket
    finally:
        socket.close()


@BP.route("/healthcheck", methods=["GET"])
def healtcheck():
    """Healthcheck endpoint."""
    return jsonify({"state": "healthy"})


@BP.route("/heating", methods=["GET"])
def heating_status():
    """Get the heating status."""
    with channel() as socket:
        socket.send_json({"command": "heating_status"})
        response = socket.recv_json()
        return make_response(response["content"], response["status"])


@BP.route("/heating/on", methods=["POST"])
def turn_heating_on():
    """Turn the heating on."""
    with channel() as socket:
        socket.send_json({"command": "turn_heating_on"})
        response = socket.recv_json()
        return make_response(response["content"], response["status"])


@BP.route("/heating/off", methods=["POST"])
def turn_heating_off():
    """Turn the heating off."""
    with channel() as socket:
        socket.send_json({"command": "turn_heating_off"})
        response = socket.recv_json()
        return make_response(response["content"], response["status"])
