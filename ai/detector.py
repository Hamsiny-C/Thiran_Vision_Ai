from ai.model import load_person_model, load_ppe_model
from ai.config import (
    PERSON_CONFIDENCE,
    PPE_CONFIDENCE,
    IMAGE_SIZE
)


person_model = load_person_model()
ppe_model = load_ppe_model()


def detect(frame, image_size=None):
    if image_size is None:
        image_size = IMAGE_SIZE

    person_results = person_model.predict(
        frame,
        conf=PERSON_CONFIDENCE,
        imgsz=image_size,
        verbose=False
    )

    ppe_results = ppe_model.predict(
        frame,
        conf=PPE_CONFIDENCE,
        imgsz=image_size,
        verbose=False
    )

    return person_results, ppe_results