from pathlib import Path
from ultralytics import YOLO


AI_DIRECTORY = Path(__file__).resolve().parent

PERSON_MODEL_PATH = AI_DIRECTORY / "models" / "yolo11n.pt"
PPE_MODEL_PATH = AI_DIRECTORY / "models" / "ppe" / "best.pt"


_person_model = None
_ppe_model = None


def load_person_model():
    global _person_model

    if _person_model is not None:
        return _person_model

    if not PERSON_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Person model not found: {PERSON_MODEL_PATH}"
        )

    _person_model = YOLO(str(PERSON_MODEL_PATH))
    return _person_model


def load_ppe_model():
    global _ppe_model

    if _ppe_model is not None:
        return _ppe_model

    if not PPE_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"PPE model not found: {PPE_MODEL_PATH}"
        )

    _ppe_model = YOLO(str(PPE_MODEL_PATH))
    return _ppe_model