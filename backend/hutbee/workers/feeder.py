# -*- coding: utf-8 -*-
"""Hutbee feeder."""
import os
import time

import kombu
from logzero import logger

from hutbee import config
from hutbee.db import DB


def store_measurement(body, message: kombu.Message):
    """Store a measurement in the database."""
    DB[config.MEASUREMENTS_COL].insert_one(body)
    logger.info(f"Measurement processed")
    message.ack()


def main():
    """Run the feeder worker."""
    user = os.environ["RABBITMQ_DEFAULT_USER"]
    password = os.environ["RABBITMQ_DEFAULT_PASS"]
    uri = f"amqp://{user}:{password}@controller:5672"

    while True:
        with kombu.Connection(uri) as connection:
            with connection.channel() as channel:
                queue = kombu.Queue("measurements.backend")
                queue.declare(channel=channel)
                queue.bind_to("measurements", channel=channel)
                consumer = connection.Consumer(queues=[queue], channel=channel)
                consumer.register_callback(store_measurement)
                consumer.consume()
        time.sleep(1)


if __name__ == "__main__":
    main()
