"""
sensor_manager.py
-----------------

Creates sensor data for any machine.
The database decides which machines exist.
"""

from sensors.generator import generate_sensor_data


def get_machine_data(machine_name):

    machine_data = {

        "machine": machine_name,

        **generate_sensor_data()

    }

    return machine_data