import os
import time
from threading import Thread

import kombu
import zmq
from kombu.mixins import ConsumerMixin
from logzero import logger
from typing import Any

from hutbee_controller.config import ZMQ_CONTEXT


class MeasurementConsumer(ConsumerMixin):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(
                queues=self.queue,
                callbacks=[self.process_measurement],
            )
        ]

    def process_measurement(self, body: Any, message: kombu.Message):
        """Store a measurement in the database."""
        # TODO: Transmit the measurement back to the safety worker
        logger.info(f"Measurement processed")
        message.ack()


class MeasurementWorker(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        user = os.environ["CONTROLLER_RABBITMQ_USERNAME"]
        password = os.environ["CONTROLLER_RABBITMQ_PASSWORD"]
        uri = f"amqp://{user}:{password}@controller-rabbitmq:5672"
        queue = kombu.Queue("measurements.safety")
        exchange = kombu.Exchange("measurements")

        while True:
            try:
                with kombu.Connection(uri) as connection:
                    with connection.channel() as channel:
                        queue.declare(channel=channel)
                        exchange.declare(channel=channel)
                        queue.bind_to("measurements", channel=channel)
                    worker = MeasurementConsumer(connection, queue)
                    worker.run()
            except ConnectionError:
                logger.warning("Connection to rabbitmq failed")
            time.sleep(60)


class SafetyWorker(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.socket = ZMQ_CONTEXT.socket(zmq.REQ)
        self.socket.connect("inproc://stream")

    def run(self):
        # For safety turn it off when restarted
        # (Additional safety in the modbus worker)
        self.socket.send_json({"command": "turn_heating_off"})
        self.socket.recv_json()

        # Start the measurement worker
        measurement_worker = MeasurementWorker()
        measurement_worker.start()

        # TODO: Once the measurement is obtained, turn off over a given temperature
