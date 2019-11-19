#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-outside-toplevel
"""Script for running hutbee controller."""

import time

import smbus

DEVICE_BUS = 1

TEMP_IN_ADDR = 0x18
TEMP_OUT_ADDR = 0x19


def read_temperature(bus, address):
    """Read the temperature in Celsius of the sensor with given address."""
    data = bus.read_i2c_block_data(address, 0x05, 2)
    temp = ((data[0] & 0x1F) * 256) + data[1]
    if temp > 4095:
        temp -= 8192
    temp = temp * 0.0625
    return temp


def main():
    bus = smbus.SMBus(DEVICE_BUS)

    while True:
        temperature_in = read_temperature(bus, TEMP_IN_ADDR)
        temperature_out = read_temperature(bus, TEMP_OUT_ADDR)
        print(temperature_in, temperature_out)
        time.sleep(1)


if __name__ == "__main__":
    main()
