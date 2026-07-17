"""
noise.py
-------------

This file simulates the noise level
of an industrial machine.
"""

import random

from sensors.config import MIN_NOISE, MAX_NOISE


def get_noise():
    """
    Generate a random noise value.
    """

    noise = random.randint(MIN_NOISE, MAX_NOISE)

    return noise


if __name__ == "__main__":
    print("Current Noise Level:", get_noise(), "dB")