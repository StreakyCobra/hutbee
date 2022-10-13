# -*- coding: utf-8 -*-
"""Hutbee feeder."""
import os
import time
from datetime import datetime, timedelta
from typing import Any

import kombu
from kombu.mixins import ConsumerMixin
from logzero import logger

from hutbee import config
from hutbee.db import DB
from hutbee.notifications import notify_managers


class Worker(ConsumerMixin):
    def __init__(self, connection, queue):
        self.connection = connection
        self.queue = queue
        self.last_notification = datetime.now()

    def get_consumers(self, Consumer, channel):
        return [
            Consumer(
                queues=self.queue,
                callbacks=[self.store_measurement, self.monitor_temperature],
            )
        ]

    def store_measurement(self, body: Any, message: kombu.Message):
        """Store a measurement in the database."""
        DB[config.MEASUREMENTS_COL].insert_one(body)
        logger.info(f"Measurement processed")
        message.ack()

    def monitor_temperature(self, body: Any, message: kombu.Message):
        """Monitor the temperature."""
        timestamp = body["date"]
        temperature = body["values"]["temperature"]
        if temperature < 5 or temperature > 15:
            # Temperature requiring attention, notifying managers
            if (datetime.now() - self.last_notification) > timedelta(minutes=1):
                notify_managers(
                    f"Temperature requires attention: {temperature}°C ({timestamp})"
                )


def main():
    """Run the feeder worker."""
    user = os.environ["CONTROLLER_RABBITMQ_USERNAME"]
    password = os.environ["CONTROLLER_RABBITMQ_PASSWORD"]
    port = os.environ["CONTROLLER_RABBITMQ_PORT"]
    uri = f"amqp://{user}:{password}@controller:{port}"
    queue = kombu.Queue("measurements.persist")
    exchange = kombu.Exchange("measurements")

    while True:
        try:
            with kombu.Connection(uri) as connection:
                with connection.channel() as channel:
                    queue.declare(channel=channel)
                    exchange.declare(channel=channel)
                    queue.bind_to("measurements", channel=channel)
                worker = Worker(connection, queue)
                worker.run()
        except ConnectionError:
            logger.warning("Connection to rabbitmq failed")
        time.sleep(60)


if __name__ == "__main__":
    main()
