"""
temperature.py
----------------

This file simulates the temperature sensor
of an industrial machine.
"""

# Import Python's random module
import random

# Import temperature limits from config.py
from sensors.config import MIN_TEMPERATURE, MAX_TEMPERATURE


def get_temperature():
    """
    Generate a random temperature value.
    """

    temperature = random.randint(MIN_TEMPERATURE, MAX_TEMPERATURE)

    return temperature


# Run this file directly for testing
if __name__ == "__main__":
    print("Current Temperature:", get_temperature(), "°C")