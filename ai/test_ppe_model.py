import os
import cv2
from ultralytics import YOLO


MODEL_PATH = "ai/models/ppe/best.pt"
IMAGE_PATH = "data/test_worker.jpg"
OUTPUT_PATH = "ai/output/ppe_model_test.jpg"


def test_ppe_model():

    if not os.path.exists(MODEL_PATH):
        print("Model file not found:", MODEL_PATH)
        return

    if not os.path.exists(IMAGE_PATH):
        print("Test image not found:", IMAGE_PATH)
        return

    os.makedirs(
        "ai/output",
        exist_ok=True
    )

    print("Loading PPE model...")

    model = YOLO(MODEL_PATH)

    print("Model classes:")
    print(model.names)

    print("\nRunning PPE detection...")

    results = model.predict(
        source=IMAGE_PATH,
        conf=0.15,
        imgsz=1280,
        verbose=False
    )

    detection_count = 0

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            detection_count += 1

            print(
                f"{detection_count}. "
                f"{class_name} - "
                f"{confidence:.2f} "
                f"Box: ({x1}, {y1}, {x2}, {y2})"
            )

        plotted_image = result.plot()

        cv2.imwrite(
            OUTPUT_PATH,
            plotted_image
        )

    print("\nTotal detections:", detection_count)
    print("Output saved at:", OUTPUT_PATH)


if __name__ == "__main__":
    test_ppe_model()