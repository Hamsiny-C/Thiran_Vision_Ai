"""
predictor.py
------------------------

Main Prediction Module
"""

from pprint import pprint

from sensors.sensor_manager import get_machine_data

from prediction.health import calculate_health
from prediction.maintenance import predict_maintenance
from prediction.fire import predict_fire


def predict_machine(sensor_data):

    health = calculate_health(
        sensor_data
    )

    maintenance = predict_maintenance(
        health
    )

    fire = predict_fire(
        sensor_data
    )

    return {

        "sensor_data": sensor_data,

        "machine_health": health,

        "maintenance": maintenance,

        "fire": fire

    }


def run_prediction(machine_name):

    sensor_data = get_machine_data(
        machine_name
    )

    return predict_machine(
        sensor_data
    )


if __name__ == "__main__":

    pprint(
        run_prediction(
            "Test Machine"
        )
    )