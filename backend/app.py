from flask import Flask, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.database import db
from backend.routes import register_routes

# Import models so SQLAlchemy knows about them
from backend.models.machine import Machine


app = Flask(__name__)

app.config.from_object(Config)

CORS(app)

db.init_app(app)


@app.route("/api/health", methods=["GET"])
def health_check():

    return jsonify({

        "status": "running",

        "service": "Thiran Vision AI Backend"

    })


register_routes(app)


if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )