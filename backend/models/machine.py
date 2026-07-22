from backend.database import db


class Machine(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    machine_name = db.Column(db.String(100))

    temperature = db.Column(db.Float)

    humidity = db.Column(db.Float)

    gas = db.Column(db.Float)

    rpm = db.Column(db.Integer)

    current = db.Column(db.Float)

    noise = db.Column(db.Float)

    vibration = db.Column(db.Float)

    health = db.Column(db.Integer)

    fire_status = db.Column(db.String(50))