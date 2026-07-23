# from backend.database import db


# class Machine(db.Model):

#     id = db.Column(db.Integer, primary_key=True)

#     machine_name = db.Column(db.String(100))

#     temperature = db.Column(db.Float)

#     humidity = db.Column(db.Float)

#     gas = db.Column(db.Float)

#     rpm = db.Column(db.Integer)

#     current = db.Column(db.Float)

#     noise = db.Column(db.Float)

#     vibration = db.Column(db.Float)

#     health = db.Column(db.Integer)

#     fire_status = db.Column(db.String(50))






from backend.database import db


class Machine(db.Model):

    __tablename__ = "machines"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    machine_code = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    machine_name = db.Column(
        db.String(100),
        nullable=False
    )

    machine_type = db.Column(
        db.String(100),
        nullable=True
    )

    location = db.Column(
        db.String(100),
        nullable=True
    )

    status = db.Column(
        db.String(20),
        default="Active"
    )

    data_source = db.Column(
        db.String(20),
        default="Simulation"
    )


    def to_dict(self):

        return {

            "id": self.id,

            "machine_code": self.machine_code,

            "machine_name": self.machine_name,

            "machine_type": self.machine_type,

            "location": self.location,

            "status": self.status,

            "data_source": self.data_source

        }