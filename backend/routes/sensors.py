from flask import Blueprint, jsonify

from backend.services.sensor_service import get_current_iot_status


sensor_routes = Blueprint(
    "sensor_routes",
    __name__
)


# Live IoT + Prediction API
@sensor_routes.route(
    "/api/iot/status",
    methods=["GET"]
)
def iot_status():

    result = get_current_iot_status()

    return jsonify(result)