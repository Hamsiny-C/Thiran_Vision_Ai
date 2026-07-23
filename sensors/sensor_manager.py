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

def get_hybrid_machine_data(
    machine_name,
    hardware_data
):

    # First generate all simulated sensor values
    machine_data = get_machine_data(
        machine_name
    )

    # Replace sensors that come from real hardware
    machine_data["temperature"] = (
        hardware_data["temperature"]
    )

    machine_data["humidity"] = (
        hardware_data["humidity"]
    )

    machine_data["gas"] = (
        hardware_data["gas"]
    )

    return machine_data