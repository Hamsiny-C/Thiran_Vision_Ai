from flask import Blueprint, jsonify

from backend.models.machine import Machine
from backend.services.sensor_service import get_current_iot_status


sensor_routes = Blueprint("sensor_routes", __name__)


# Live IoT + Prediction API

@sensor_routes.route("/api/iot/status", methods=["GET"])
def iot_status():

    result = get_current_iot_status()

    return jsonify(result)


# Get all stored machine readings

@sensor_routes.route("/api/machines", methods=["GET"])
def get_machines():

    machines = Machine.query.all()

    result = []

    for machine in machines:

        result.append({

            "id": machine.id,

            "machine_name": machine.machine_name,

            "temperature": machine.temperature,

            "humidity": machine.humidity,

            "gas": machine.gas,

            "rpm": machine.rpm,

            "current": machine.current,

            "noise": machine.noise,

            "vibration": machine.vibration,

            "health": machine.health,

            "fire_status": machine.fire_status

        })

    return jsonify(result)


# Get one machine record

@sensor_routes.route("/api/machines/<int:id>", methods=["GET"])
def get_machine(id):

    machine = Machine.query.get(id)

    if machine is None:

        return jsonify({
            "message": "Machine not found"
        }), 404

    return jsonify({

        "id": machine.id,

        "machine_name": machine.machine_name,

        "temperature": machine.temperature,

        "humidity": machine.humidity,

        "gas": machine.gas,

        "rpm": machine.rpm,

        "current": machine.current,

        "noise": machine.noise,

        "vibration": machine.vibration,

        "health": machine.health,

        "fire_status": machine.fire_status

    })