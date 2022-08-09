import time
from threading import Thread

import zmq

from hutbee_controller.config import ZMQ_CONTEXT


class WatchdogWorker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.socket = ZMQ_CONTEXT.socket(zmq.REQ)
        self.socket.connect("inproc://stream")
        self.state = False

    def run(self):
        while True:
            self.state = not self.state
            self.socket.send_json({"command": "set_watchdog", "value": self.state})
            self.socket.recv_json()
            time.sleep(1)
