class Config:

    SQLALCHEMY_DATABASE_URI = "sqlite:///thiran.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Arduino Serial Configuration
    ARDUINO_PORT = None
    ARDUINO_BAUD_RATE = 9600