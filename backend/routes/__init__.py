from backend.routes.sensors import sensor_routes
from backend.routes.machines import machines_bp


def register_routes(app):

    app.register_blueprint(sensor_routes)
    app.register_blueprint(machines_bp)