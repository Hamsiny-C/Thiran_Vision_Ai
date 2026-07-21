import cv2

from tracking.config import (
    WORKER_COLOR,
    TEXT_COLOR,
    FONT_SCALE,
    BOX_THICKNESS
)


def draw_worker(frame, worker):
    """
    Draw worker ID and position.
    """

    x, y = worker.center

    # Draw worker center
    cv2.circle(
        frame,
        (int(x), int(y)),
        5,
        WORKER_COLOR,
        -1
    )

    # Draw worker ID
    cv2.putText(
        frame,
        f"Worker {worker.id}",
        (int(x) + 10, int(y) - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        FONT_SCALE,
        TEXT_COLOR,
        2
    )

    # Draw movement path
    if len(worker.path) > 1:

        for i in range(1, len(worker.path)):

            cv2.line(
                frame,
                (
                    int(worker.path[i - 1][0]),
                    int(worker.path[i - 1][1])
                ),
                (
                    int(worker.path[i][0]),
                    int(worker.path[i][1])
                ),
                WORKER_COLOR,
                2
            )

    return frame


def draw_workers(frame, workers):
    """
    Draw all tracked workers.
    """

    for worker in workers.values():

        frame = draw_worker(
            frame,
            worker
        )

    return frame


def draw_alerts(frame, alerts):
    """
    Draw alert messages.
    """

    y = 30

    for alert in alerts:

        cv2.putText(
            frame,
            alert,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2
        )

        y += 30

    return frame

def draw_dashboard(frame, worker_count, ppe_summary):
    """
    Draw dashboard with worker and PPE information.
    """

    # Background
    cv2.rectangle(
        frame,
        (10, 10),
        (330, 250),
        (40, 40, 40),
        -1
    )

    # Border
    cv2.rectangle(
        frame,
        (10, 10),
        (330, 250),
        (255, 255, 0),
        2
    )

    # Title
    cv2.putText(
        frame,
        "THIRAN VISION AI",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 0),
        2
    )

    cv2.putText(
        frame,
        "INDUSTRIAL PPE MONITORING",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.45,
        (255, 255, 255),
        1
    )

    # Line
    cv2.line(
        frame,
        (20, 75),
        (310, 75),
        (255, 255, 255),
        1
    )

    # Worker Count
    cv2.putText(
        frame,
        f"Workers : {worker_count}",
        (20, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    # Safe Workers
    safe = min(
        ppe_summary["hardhat"],
        ppe_summary["safety_vest"]
    )

    unsafe = worker_count - safe

    cv2.putText(
        frame,
        f"Safe : {safe}",
        (20, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Unsafe : {unsafe}",
        (180, 130),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2
    )

    # Helmet
    cv2.putText(
        frame,
        f"Helmet YES : {ppe_summary['hardhat']}",
        (20, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Helmet NO : {ppe_summary['no_hardhat']}",
        (180, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 255),
        2
    )

    # Vest
    cv2.putText(
        frame,
        f"Vest YES : {ppe_summary['safety_vest']}",
        (20, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        f"Vest NO : {ppe_summary['no_safety_vest']}",
        (180, 190),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 255),
        2
    )

    # Check PPE
    check_ppe = min(
        ppe_summary["hardhat"],
        ppe_summary["safety_vest"]
    )

    cv2.putText(
        frame,
        f"Check PPE : {check_ppe}",
        (20, 220),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        2
    )

    return frame  