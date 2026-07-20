"""
health.py
------------------------

Calculates the machine health
based on sensor values.
"""

from prediction.model import (
    HIGH_TEMPERATURE,
    HIGH_GAS,
    HIGH_CURRENT,
    HIGH_VIBRATION,
    HIGH_NOISE,
    HIGH_RPM,
    MAX_HEALTH
)


def calculate_health(sensor_data):
    """
    Calculate machine health.
    """

    health = MAX_HEALTH

    if sensor_data["temperature"] > HIGH_TEMPERATURE:
        health -= 20

    if sensor_data["gas"] > HIGH_GAS:
        health -= 20

    if sensor_data["current"] > HIGH_CURRENT:
        health -= 15

    if sensor_data["vibration"] > HIGH_VIBRATION:
        health -= 25

    if sensor_data["noise"] > HIGH_NOISE:
        health -= 10

    if sensor_data["rpm"] > HIGH_RPM:
        health -= 10

    if health < 0:
        health = 0

    return health

if __name__ == "__main__":

    sample_data = {
        "temperature": 85,
        "humidity": 70,
        "gas": 165,
        "rpm": 1900,
        "current": 24,
        "noise": 90,
        "vibration": 2.4
    }

    print("Machine Health:", calculate_health(sample_data), "%")