import zmq
from flask import Flask

from hutbee_controller.controller import BP
from hutbee_controller.modbus import ModbusWorker
from hutbee_controller.watchdog import WatchdogWorker

APP = Flask(__name__)


def main():
    worker = ModbusWorker()
    worker.start()

    watchdog = WatchdogWorker()
    watchdog.start()

    APP.register_blueprint(BP)
    APP.run(host="0.0.0.0", port="80")


if __name__ == "__main__":
    main()
