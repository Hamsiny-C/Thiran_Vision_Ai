from backend.database import db

from backend.models.machine import Machine
from backend.models.sensor_reading import SensorReading

from sensors.sensor_manager import get_machine_data

from prediction.predictor import predict_machine


def get_current_iot_status():

    # Get all active machines from database
    machines = Machine.query.filter_by(
        status="Active"
    ).all()

    results = []

    # Process each active machine
    for machine in machines:

        # For now, process simulation machines
        if machine.data_source == "Simulation":

            # Generate sensor data dynamically
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

            # Prepare reading for database storage
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

    # Save all readings
    db.session.commit()

    return results