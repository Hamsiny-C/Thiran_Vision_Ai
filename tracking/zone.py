import cv2
import numpy as np

from tracking.config import (
    RESTRICTED_ZONE,
    ZONE_COLOR,
    LINE_THICKNESS
)


def get_zone_polygon():
    """
    Convert restricted-zone points
    into the format required by OpenCV.
    """
    return np.array(
        RESTRICTED_ZONE,
        dtype=np.int32
    )


def draw_restricted_zone(frame):
    """
    Draw the restricted zone polygon.
    """

    polygon = get_zone_polygon()

    cv2.polylines(
        frame,
        [polygon],
        True,
        ZONE_COLOR,
        LINE_THICKNESS
    )

    first_x, first_y = RESTRICTED_ZONE[0]

    cv2.putText(
        frame,
        "RESTRICTED ZONE",
        (first_x, max(first_y - 10, 25)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        ZONE_COLOR,
        2,
        cv2.LINE_AA
    )

    return frame


def point_inside_zone(point):
    """
    Check whether a worker is inside
    the restricted zone.
    """

    polygon = get_zone_polygon()

    point_x = float(point[0])
    point_y = float(point[1])

    result = cv2.pointPolygonTest(
        polygon,
        (point_x, point_y),
        False
    )

    return result >= 0


def update_zone_status(workers):
    """
    Update every worker's restricted-zone status.
    """

    alerts = []

    for worker in workers.values():

        inside_zone = point_inside_zone(
            worker.center
        )

        worker.in_restricted_zone = inside_zone

        if inside_zone:
            alerts.append(
                f"Worker {worker.id} entered restricted zone"
            )

    return alerts 