# -*- coding: utf-8 -*-
"""Hutbee feeder."""
import os
import time
from typing import Any

import kombu
from kombu.mixins import ConsumerMixin
from logzero import logger

from hutbee import config
from hutbee.db import DB


class Worker(ConsumerMixin):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(
                queues=self.queue,
                callbacks=[self.store_measurement],
            )
        ]

    def store_measurement(self, body: Any, message: kombu.Message):
        """Store a measurement in the database."""
        DB[config.MEASUREMENTS_COL].insert_one(body)
        logger.info(f"Measurement processed")
        message.ack()


def main():
    """Run the feeder worker."""
    user = os.environ["RABBITMQ_DEFAULT_USER"]
    password = os.environ["RABBITMQ_DEFAULT_PASS"]
    uri = f"amqp://{user}:{password}@controller:5672"
    queue = kombu.Queue("measurements.backend")

    while True:
        try:
            with kombu.Connection(uri) as connection:
                with connection.channel() as channel:
                    queue.declare(channel=channel)
                    queue.bind_to("measurements", channel=channel)
                worker = Worker(connection, queue)
                worker.run()
        except ConnectionRefusedError as e:
            logger.warning("Connection to rabbitmq failed")
        time.sleep(1)


if __name__ == "__main__":
    main()
