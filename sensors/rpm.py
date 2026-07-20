"""
rpm.py
-------------

This file simulates the RPM
(Revolutions Per Minute)
of an industrial machine.
"""

import random

from sensors.config import MIN_RPM, MAX_RPM


def get_rpm():
    """
    Generate a random RPM value.
    """

    rpm = random.randint(MIN_RPM, MAX_RPM)

    return rpm


if __name__ == "__main__":
    print("Current RPM:", get_rpm(), "RPM")