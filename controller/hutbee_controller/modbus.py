import os
from threading import Thread

import zmq
from pymodbus.client.sync import ModbusTcpClient

from hutbee_controller.config import ZMQ_CONTEXT


class ModbusWorker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self._client = ModbusTcpClient(os.environ["MODBUS_SERVER_HOST"])
        self._socket = ZMQ_CONTEXT.socket(zmq.REP)

    def run(self):
        self._socket.bind("inproc://stream")
        while True:
            args = self._socket.recv_json()
            result = self._execute(args)
            self._socket.send_json(result)

    def _execute(self, args):
        command = args.get("command")
        match command:
            case "set_watchdog":
                return self._set_watchdog(args["value"])
            case "heating_status":
                return self._heating_status()
            case "turn_heating_on":
                return self._turn_heating_on()
            case "turn_heating_off":
                return self._turn_heating_off()
            case _:
                return {
                    "content": {"message": "Unknown command"},
                    "status": 400,
                }

    def _set_watchdog(self, value):
        try:
            self._client.write_coil(0, int(value))
            return {
                "content": {"message": f"The watchdog has been set to {value}"},
                "status": 200,
            }
        except:
            return {
                "content": {"message": f"Can not set the watchdog to {value}"},
                "status": 400,
            }

    def _heating_status(self):
        try:
            coils = self._client.read_coils(80, 8).bits
            heater = "ON" if coils[1] else "OFF"
            pump = "ON" if coils[2] else "OFF"
            return {
                "content": {"heater": heater, "pump": pump},
                "status": 200,
            }
        except:
            return {
                "content": {"message": "Can not access the heating status"},
                "status": 400,
            }

    def _turn_heating_on(self):
        try:
            self._client.write_coil(1, 1)
            return {
                "content": {"message": "The heating has been turned on"},
                "status": 200,
            }
        except:
            return {
                "content": {"message": "Can not turn the heating on"},
                "status": 400,
            }

    def _turn_heating_off(self):
        try:
            self._client.write_coil(1, 0)
            return {
                "content": {"message": "The heating has been turned off"},
                "status": 200,
            }
        except:
            return {
                "content": {"message": "Can not turn the heating off"},
                "status": 400,
            }
