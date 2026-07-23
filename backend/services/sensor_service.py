from backend.database import db

from backend.models import machine
from backend.models.machine import Machine
from backend.models.sensor_reading import SensorReading
from backend.config import Config
from sensors import temperature
from sensors.sensor_manager import (
    get_machine_data,
    get_hybrid_machine_data
)

from hardware.arduino_reader import (
    get_sensor_data_with_fallback
)

from prediction.predictor import predict_machine

from backend.config import Config

from hardware.arduino_reader import get_sensor_data_with_fallback


def get_current_iot_status():

    # Get all active machines from database
    machines = Machine.query.filter_by(
        status="Active"
    ).all()

    results = []

    # Process each active machine
    for machine in machines:

        # Choose sensor source based on machine configuration
        if machine.data_source == "Hardware":

            # Get DHT22 + MQ-2 data.
            # Since Arduino is not connected yet,
            # this currently returns fallback/mock data.
            hardware_data = get_sensor_data_with_fallback(
                port=Config.ARDUINO_PORT
            )

            # Combine hardware values with
            # remaining simulated sensors
            sensor_data = get_hybrid_machine_data(
                machine.machine_name,
                hardware_data
            )

        else:

            # Fully simulated machine
            sensor_data = get_machine_data(
                machine.machine_name
        )

        # Run health, maintenance and fire prediction
        prediction = predict_machine(
            sensor_data
        )

        # Create historical sensor reading
        reading = SensorReading(

            machine_id=machine.id,

            temperature=sensor_data["temperature"],

            humidity=sensor_data["humidity"],

            gas=sensor_data["gas"],

            rpm=sensor_data["rpm"],

            current=sensor_data["current"],

            noise=sensor_data["noise"],

            vibration=sensor_data["vibration"],

            health=prediction["machine_health"],

            fire_status=prediction["fire"]["fire_status"]
        )

        # Add reading to database session
        db.session.add(reading)

        # Prepare API response
        results.append({

            "machine": {

                "id": machine.id,

                "machine_code":
                    machine.machine_code,

                "machine_name":
                    machine.machine_name,

                "machine_type":
                    machine.machine_type,

                "location":
                    machine.location,

                "status":
                    machine.status,

                "data_source":
                    machine.data_source
            },

            "sensor_data":
                sensor_data,

            "machine_health":
                prediction["machine_health"],

            "maintenance":
                prediction["maintenance"],

            "fire":
                prediction["fire"]
        })

    # Save readings for all processed machines
    db.session.commit()

    return results