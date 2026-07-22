from prediction.predictor import run_prediction

from backend.database import db
from backend.models.machine import Machine


def get_current_iot_status():

    result = run_prediction()

    sensor = result["sensor_data"]

    machine = Machine(

        machine_name=sensor["machine"],

        temperature=sensor["temperature"],

        humidity=sensor["humidity"],

        gas=sensor["gas"],

        rpm=sensor["rpm"],

        current=sensor["current"],

        noise=sensor["noise"],

        vibration=sensor["vibration"],

        health=result["machine_health"],

        fire_status=result["fire"]["fire_status"]
    )

    db.session.add(machine)

    db.session.commit()

    return result