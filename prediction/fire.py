"""
fire.py
------------------------

Predict Fire Risk
"""

from prediction.model import FIRE_TEMPERATURE, FIRE_GAS


def predict_fire(sensor_data):
    """
    Predict fire risk using temperature and gas values.
    """

    risk = 0

    if sensor_data["temperature"] >= FIRE_TEMPERATURE:
        risk += 50

    if sensor_data["gas"] >= FIRE_GAS:
        risk += 50

    if risk >= 80:
        status = "Critical"

    elif risk >= 50:
        status = "High"

    elif risk >= 20:
        status = "Medium"

    else:
        status = "Low"

    return {
        "fire_risk": risk,
        "fire_status": status
    }


if __name__ == "__main__":

    sample = {
        "temperature": 90,
        "gas": 180
    }

    print(predict_fire(sample))