"""
sensor_manager.py
-------------------

Manages all virtual sensor data.
"""

import json

from sensors.generator import generate_sensor_data
from sensors.config import MACHINE_NAME


def get_machine_data():

    machine_data = {
        "machine": MACHINE_NAME,
        **generate_sensor_data()
    }

    return machine_data


if __name__ == "__main__":
    print(json.dumps(get_machine_data(), indent=4))