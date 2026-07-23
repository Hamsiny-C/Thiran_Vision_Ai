import json
import serial

def parse_temperature(line):
    """
    Convert Arduino temperature output
    such as TEMP:31.5 into a float.
    """

    if not line.startswith("TEMP:"):
        return None

    try:
        value = line.split(":")[1]
        return float(value)

    except (ValueError, IndexError):
        return None


def read_temperature_from_arduino(
    port,
    baud_rate=9600
):
    """
    Read one temperature value from Arduino.

    Example Arduino output:
    TEMP:31.5
    """

    connection = serial.Serial(
        port=port,
        baudrate=baud_rate,
        timeout=2
    )

    line = connection.readline()

    decoded_line = line.decode(
        "utf-8"
    ).strip()

    connection.close()

    return parse_temperature(decoded_line)

def get_temperature_with_fallback(
    port=None,
    fallback_temperature=31.5
):

    # If no Arduino port has been configured yet,
    # use mock temperature.
    if not port:

        return fallback_temperature

    try:

        temperature = read_temperature_from_arduino(
            port
        )

        # Arduino responded, but data was invalid
        if temperature is None:

            return fallback_temperature

        # Valid real Arduino temperature
        return temperature

    except (
        serial.SerialException,
        OSError
    ):

        # Arduino disconnected / wrong COM port /
        # serial communication unavailable
        return fallback_temperature

    

def parse_sensor_data(line):

    try:

        data = json.loads(line)

        temperature = float(
            data["temperature"]
        )

        humidity = float(
            data["humidity"]
        )

        gas = float(
            data["gas"]
        )

        return {
            "temperature": temperature,
            "humidity": humidity,
            "gas": gas
        }

    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError
    ):

        return None

def read_sensor_data_from_arduino(
    port,
    baud_rate=9600
):

    connection = serial.Serial(
        port=port,
        baudrate=baud_rate,
        timeout=2
    )

    try:

        line = connection.readline()

        decoded_line = line.decode(
            "utf-8"
        ).strip()

        return parse_sensor_data(
            decoded_line
        )

    finally:

        connection.close()

def get_sensor_data_with_fallback(
    port=None
):

    fallback_data = {

        "temperature": 31.5,

        "humidity": 62.0,

        "gas": 120.0

    }

    # No Arduino configured
    if not port:

        return fallback_data

    try:

        sensor_data = (
            read_sensor_data_from_arduino(
                port
            )
        )

        if sensor_data is None:

            return fallback_data

        return sensor_data

    except (
        serial.SerialException,
        OSError
    ):

        return fallback_data