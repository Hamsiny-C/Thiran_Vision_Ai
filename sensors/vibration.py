"""
vibration.py
-------------

This file simulates the vibration level
of an industrial machine.
"""

import random

from sensors.config import MIN_VIBRATION, MAX_VIBRATION


def get_vibration():
    """
    Generate a random vibration value.
    """

    vibration = round(
        random.uniform(MIN_VIBRATION, MAX_VIBRATION),
        2
    )

    return vibration


if __name__ == "__main__":
    print("Current Vibration:", get_vibration(), "RMS")