import cv2

from ai.config import (
    CAMERA_ID,
    CAMERA_IMAGE_SIZE,
    PROCESS_EVERY_N_FRAMES
)
from ai.detector import detect
from ai.ppe_checker import count_workers, analyze_ppe
from ai.visualizer import draw_detection_dashboard


def start_camera():
    camera = cv2.VideoCapture(
        CAMERA_ID,
        cv2.CAP_DSHOW
    )

    if not camera.isOpened():
        print("Error: Camera could not be opened.")
        return

    # Reduce camera resolution for smoother motion
    camera.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        640
    )

    camera.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        480
    )

    camera.set(
        cv2.CAP_PROP_FPS,
        30
    )

    # Keep only the latest camera frame
    camera.set(
        cv2.CAP_PROP_BUFFERSIZE,
        1
    )

    print("THIRAN VISION AI camera started.")
    print("Press Q to close the camera.")

    frame_number = 0
    last_processed_frame = None

    while True:
        success, frame = camera.read()

        if not success:
            print("Error: Could not read camera frame.")
            break

        frame_number += 1

        # Run AI once every two frames
        if (
            frame_number % PROCESS_EVERY_N_FRAMES == 0
            or last_processed_frame is None
        ):
            person_results, ppe_results = detect(
                frame,
                image_size=CAMERA_IMAGE_SIZE
            )

            worker_count = count_workers(
                person_results
            )

            ppe_summary = analyze_ppe(
                ppe_results
            )

            last_processed_frame = draw_detection_dashboard(
                image=frame,
                person_results=person_results,
                ppe_results=ppe_results,
                worker_count=worker_count,
                ppe_summary=ppe_summary
            )

        cv2.imshow(
            "THIRAN VISION AI - Live Safety Monitoring",
            last_processed_frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()

    print("Camera closed.")


if __name__ == "__main__":
    start_camera()