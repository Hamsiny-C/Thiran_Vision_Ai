import cv2

from ai.detector import detect
from ai.ppe_checker import (
    analyze_ppe,
    count_workers
)

from tracking.tracker import Tracker
from tracking.zone import (
    draw_restricted_zone,
    update_zone_status
)
from tracking.behavior import (
    update_worker_behavior
)
from tracking.utils import (
    draw_workers,
    draw_dashboard,
    draw_alerts
)


tracker = Tracker()


def get_person_centers(person_results):
    """
    Convert YOLO detections into
    center points.
    """

    centers = []

    for result in person_results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])

            if result.names[class_id] != "person":
                continue

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            center = (
                int((x1 + x2) / 2),
                int((y1 + y2) / 2)
            )

            centers.append(center)

    return centers


def start_tracking(camera=0):

    video = cv2.VideoCapture(camera)

    if not video.isOpened():

        print("Unable to open camera.")

        return

    print("Tracking Started")
    print("Press Q to quit.")

    while True:

        success, frame = video.read()

        if not success:
            break

        # AI Detection
        person_results, ppe_results = detect(frame)
        worker_count = count_workers(person_results)

        ppe_summary = analyze_ppe(ppe_results)


        centers = get_person_centers(
            person_results
        )

        # Tracking
        workers = tracker.update(
            centers
        )

        # Restricted Zone
        zone_alerts = update_zone_status(
            workers
        )

        # Behaviour Analysis
        behaviour_alerts = update_worker_behavior(
            workers
        )

        alerts = zone_alerts + behaviour_alerts

        # Draw Everything
        frame = draw_restricted_zone(
            frame
        )

        frame = draw_workers(
            frame,
            workers
        )

        frame = draw_dashboard(
            frame,
           worker_count,
           ppe_summary
   )
        frame = draw_alerts(
            frame,
            alerts
        )

        cv2.imshow(
            "THIRAN VISION AI - Worker Tracking",
            frame
        )

        key = cv2.waitKey(1)

        if key == ord("q"):
            break

    video.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":

    start_tracking() 