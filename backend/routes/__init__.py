from backend.routes.sensors import sensor_routes


def register_routes(app):

    app.register_blueprint(sensor_routes)