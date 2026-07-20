"""
current.py
-------------

This file simulates the electrical current
consumed by an industrial machine.
"""

import random

from sensors.config import MIN_CURRENT, MAX_CURRENT


def get_current():
    """
    Generate a random current value.
    """

    current = random.randint(MIN_CURRENT, MAX_CURRENT)

    return current


if __name__ == "__main__":
    print("Current Consumption:", get_current(), "A")