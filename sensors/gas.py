"""
gas.py
-------------

This file simulates the gas sensor
of an industrial machine.
"""

import random

from sensors.config import MIN_GAS, MAX_GAS


def get_gas():
    """
    Generate a random gas value.
    """

    gas = random.randint(MIN_GAS, MAX_GAS)

    return gas


if __name__ == "__main__":
    print("Current Gas Level:", get_gas(), "ppm")