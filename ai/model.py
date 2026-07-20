from ultralytics import YOLO


def load_person_model():
    return YOLO("ai/models/yolo11n.pt")


def load_ppe_model():
    return YOLO("ai/models/ppe/best.pt")