"""
predictor.py
------------------------

Main Prediction Module
"""

from sensors.sensor_manager import get_machine_data

from prediction.health import calculate_health
from prediction.maintenance import predict_maintenance
from prediction.fire import predict_fire


def run_prediction():

    sensor_data = get_machine_data()

    health = calculate_health(sensor_data)

    maintenance = predict_maintenance(health)

    fire = predict_fire(sensor_data)

    result = {

        "sensor_data": sensor_data,

        "machine_health": health,

        "maintenance": maintenance,

        "fire": fire

    }

    return result


if __name__ == "__main__":

    from pprint import pprint

    pprint(run_prediction())