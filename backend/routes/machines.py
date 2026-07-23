from flask import Blueprint, jsonify, request

from backend.database import db
from backend.models.machine import Machine

from backend.models.sensor_reading import SensorReading


machines_bp = Blueprint(
    "machines",
    __name__
)


@machines_bp.route(
    "/api/machines",
    methods=["POST"]
)
def add_machine():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "No machine data provided"
        }), 400

    machine_name = data.get("machine_name")

    if not machine_name:
        return jsonify({
            "error": "machine_name is required"
        }), 400

    # Generate next machine code
    last_machine = Machine.query.order_by(
        Machine.id.desc()
    ).first()

    if last_machine:

        next_number = last_machine.id + 1

    else:

        next_number = 1

    machine_code = f"M{next_number:03d}"

    new_machine = Machine(

        machine_code=machine_code,

        machine_name=machine_name,

        machine_type=data.get(
            "machine_type"
        ),

        location=data.get(
            "location"
        ),

        status="Active",

        data_source=data.get(
            "data_source",
            "Simulation"
        )
    )

    db.session.add(new_machine)

    db.session.commit()

    return jsonify({

        "message": "Machine added successfully",

        "machine": new_machine.to_dict()

    }), 201


@machines_bp.route(
    "/api/machines",
    methods=["GET"]
)
def get_machines():

    machines = Machine.query.all()

    return jsonify({

        "count": len(machines),

        "machines": [
            machine.to_dict()
            for machine in machines
        ]

    }), 200

@machines_bp.route(
    "/api/machines/<int:machine_id>",
    methods=["GET"]
)
def get_machine(machine_id):

    machine = db.session.get(
        Machine,
        machine_id
    )

    if not machine:

        return jsonify({
            "error": "Machine not found"
        }), 404

    return jsonify({

        "machine": machine.to_dict()

    }), 200

@machines_bp.route(
    "/api/machines/<int:machine_id>",
    methods=["PUT"]
)
def update_machine(machine_id):

    machine = db.session.get(
        Machine,
        machine_id
    )

    if not machine:

        return jsonify({
            "error": "Machine not found"
        }), 404

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "No update data provided"
        }), 400

    machine.machine_name = data.get(
        "machine_name",
        machine.machine_name
    )

    machine.machine_type = data.get(
        "machine_type",
        machine.machine_type
    )

    machine.location = data.get(
        "location",
        machine.location
    )

    machine.data_source = data.get(
        "data_source",
        machine.data_source
    )

    db.session.commit()

    return jsonify({

        "message":
            "Machine updated successfully",

        "machine":
            machine.to_dict()

    }), 200

@machines_bp.route(
    "/api/machines/<int:machine_id>/deactivate",
    methods=["PATCH"]
)
def deactivate_machine(machine_id):

    machine = db.session.get(
        Machine,
        machine_id
    )

    if not machine:

        return jsonify({
            "error": "Machine not found"
        }), 404

    machine.status = "Inactive"

    db.session.commit()

    return jsonify({

        "message":
            "Machine deactivated successfully",

        "machine":
            machine.to_dict()

    }), 200

@machines_bp.route(
    "/api/machines/<int:machine_id>/readings",
    methods=["GET"]
)
def get_machine_readings(machine_id):

    machine = db.session.get(
        Machine,
        machine_id
    )

    if not machine:

        return jsonify({
            "error": "Machine not found"
        }), 404

    readings = SensorReading.query.filter_by(
        machine_id=machine_id
    ).order_by(
        SensorReading.created_at.desc()
    ).all()

    return jsonify({

        "machine": machine.to_dict(),

        "reading_count": len(readings),

        "readings": [
            reading.to_dict()
            for reading in readings
        ]

    }), 200

@machines_bp.route(
    "/api/machines/<int:machine_id>/status",
    methods=["GET"]
)
def get_machine_status(machine_id):

    machine = db.session.get(
        Machine,
        machine_id
    )

    if not machine:

        return jsonify({
            "error": "Machine not found"
        }), 404

    latest_reading = SensorReading.query.filter_by(
        machine_id=machine_id
    ).order_by(
        SensorReading.created_at.desc()
    ).first()

    if not latest_reading:

        return jsonify({

            "machine": machine.to_dict(),

            "message":
                "No sensor readings available"

        }), 200

    return jsonify({

        "machine": machine.to_dict(),

        "latest_status":
            latest_reading.to_dict()

    }), 200

@machines_bp.route(
    "/api/machines/<int:machine_id>/activate",
    methods=["PATCH"]
)
def activate_machine(machine_id):

    machine = db.session.get(
        Machine,
        machine_id
    )

    if not machine:

        return jsonify({
            "error": "Machine not found"
        }), 404

    machine.status = "Active"

    db.session.commit()

    return jsonify({

        "message":
            "Machine activated successfully",

        "machine":
            machine.to_dict()

    }), 200