from datetime import datetime

from backend.database import db


class SensorReading(db.Model):

    __tablename__ = "sensor_readings"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    machine_id = db.Column(
        db.Integer,
        db.ForeignKey("machines.id"),
        nullable=False
    )

    temperature = db.Column(db.Float)

    humidity = db.Column(db.Float)

    gas = db.Column(db.Float)

    rpm = db.Column(db.Integer)

    current = db.Column(db.Float)

    noise = db.Column(db.Float)

    vibration = db.Column(db.Float)

    health = db.Column(db.Integer)

    fire_status = db.Column(db.String(50))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    def to_dict(self):

        return {

            "id": self.id,

            "machine_id": self.machine_id,

            "temperature": self.temperature,

            "humidity": self.humidity,

            "gas": self.gas,

            "rpm": self.rpm,

            "current": self.current,

            "noise": self.noise,

            "vibration": self.vibration,

            "health": self.health,

            "fire_status": self.fire_status,

            "created_at":
                self.created_at.isoformat()
                if self.created_at
                else None
        }