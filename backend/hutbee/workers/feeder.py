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
    def __init__(self, connection, queue, notifier):
        self.connection = connection
        self.queue = queue
        self.notifier = notifier

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
        self.notifier.publish({"username": "fabien", "message": body["temperature"]})
        logger.info(f"Measurement processed")
        message.ack()


def setup_notifier():
    user = os.environ["BACKEND_RABBITMQ_USERNAME"]
    password = os.environ["BACKEND_RABBITMQ_PASSWORD"]
    uri = f"amqp://{user}:{password}@backend-rabbitmq:5672"
    with kombu.Connection(
        uri, transport_options={"confirm_publish": True}
    ) as connection:
        exchange = kombu.Exchange("notify")(connection)
        exchange.declare()
        producer = connection.Producer(exchange=exchange)
        return producer


def main():
    """Run the feeder worker."""
    user = os.environ["CONTROLLER_RABBITMQ_USERNAME"]
    password = os.environ["CONTROLLER_RABBITMQ_PASSWORD"]
    port = os.environ["CONTROLLER_RABBITMQ_PORT"]
    uri = f"amqp://{user}:{password}@controller:{port}"
    queue = kombu.Queue("measurements.persist")

    notifier = setup_notifier()

    while True:
        try:
            with kombu.Connection(uri) as connection:
                with connection.channel() as channel:
                    queue.declare(channel=channel)
                    queue.bind_to("measurements", channel=channel)
                worker = Worker(connection, queue, notifier)
                worker.run()
        except ConnectionError:
            logger.warning("Connection to rabbitmq failed")
        time.sleep(60)


if __name__ == "__main__":
    main()
