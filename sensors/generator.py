"""
generator.py
-----------------

Collects data from all virtual sensors.
"""

from sensors.temperature import get_temperature
from sensors.humidity import get_humidity
from sensors.gas import get_gas
from sensors.rpm import get_rpm
from sensors.current import get_current
from sensors.noise import get_noise
from sensors.vibration import get_vibration


def generate_sensor_data():

    sensor_data = {
        "temperature": get_temperature(),
        "humidity": get_humidity(),
        "gas": get_gas(),
        "rpm": get_rpm(),
        "current": get_current(),
        "noise": get_noise(),
        "vibration": get_vibration()
    }

    return sensor_data


if __name__ == "__main__":
    print(generate_sensor_data())