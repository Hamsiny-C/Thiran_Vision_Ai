from ai.model import (
    load_person_model,
    load_ppe_model
)

from ai.config import (
    IMAGE_PERSON_CONFIDENCE,
    IMAGE_PPE_CONFIDENCE,
    IMAGE_SIZE,
    VIDEO_PERSON_CONFIDENCE,
    VIDEO_PPE_CONFIDENCE,
    VIDEO_IMAGE_SIZE,
    CAMERA_PERSON_CONFIDENCE,
    CAMERA_PPE_CONFIDENCE,
    CAMERA_IMAGE_SIZE,
    PERSON_IOU,
    PPE_IOU
)


person_model = load_person_model()
ppe_model = load_ppe_model()


def detect(
    frame,
    mode="image",
    image_size=None
):
    """
    Detect people and PPE.

    mode:
        image
        video
        camera
    """

    if frame is None:
        raise ValueError(
            "Input frame cannot be None."
        )

    mode = mode.lower().strip()

    if mode == "camera":
        person_confidence = CAMERA_PERSON_CONFIDENCE
        ppe_confidence = CAMERA_PPE_CONFIDENCE

        if image_size is None:
            image_size = CAMERA_IMAGE_SIZE

    elif mode == "video":
        person_confidence = VIDEO_PERSON_CONFIDENCE
        ppe_confidence = VIDEO_PPE_CONFIDENCE

        if image_size is None:
            image_size = VIDEO_IMAGE_SIZE

    else:
        person_confidence = IMAGE_PERSON_CONFIDENCE
        ppe_confidence = IMAGE_PPE_CONFIDENCE

        if image_size is None:
            image_size = IMAGE_SIZE

    person_results = person_model.predict(
        source=frame,
        conf=person_confidence,
        iou=PERSON_IOU,
        imgsz=image_size,
        classes=[0],
        max_det=100,
        agnostic_nms=False,
        verbose=False
    )

    ppe_results = ppe_model.predict(
        source=frame,
        conf=ppe_confidence,
        iou=PPE_IOU,
        imgsz=image_size,
        max_det=200,
        agnostic_nms=False,
        verbose=False
    )

    return person_results, ppe_results