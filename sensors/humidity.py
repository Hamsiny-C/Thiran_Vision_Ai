"""
humidity.py
----------------

This file simulates the humidity sensor
of an industrial machine.
"""

# Import Python's random module
import random

# Import humidity limits from config.py
from sensors.config import MIN_HUMIDITY, MAX_HUMIDITY


def get_humidity():
    """
    Generate a random humidity value.
    """

    humidity = random.randint(MIN_HUMIDITY, MAX_HUMIDITY)

    return humidity


# Run this file directly for testing
if __name__ == "__main__":
    print("Current Humidity:", get_humidity(), "%")