import time

from tracking.config import (
    IDLE_TIME_THRESHOLD,
    LOITERING_TIME_THRESHOLD
)


def update_worker_behavior(workers):
    """
    Update worker behavior such as
    idle detection and loitering.
    """

    alerts = []

    current_time = time.time()

    for worker in workers.values():

        # Update idle state
        worker.update_idle(
            IDLE_TIME_THRESHOLD
        )

        if worker.is_idle:

            alerts.append(
                f"Worker {worker.id} is idle."
            )

        # Loitering detection
        visible_time = (
            current_time -
            worker.first_seen
        )

        if visible_time >= LOITERING_TIME_THRESHOLD:

            alerts.append(
                f"Worker {worker.id} loitering."
            )

    return alerts


def worker_speed(worker):
    """
    Calculate worker movement speed.
    """

    x1, y1 = worker.previous_center
    x2, y2 = worker.center

    return ((x2 - x1) ** 2 +
            (y2 - y1) ** 2) ** 0.5


def moving(worker):
    """
    Returns True if worker is moving.
    """

    return worker_speed(worker) > 5


def stopped(worker):
    """
    Returns True if worker is stationary.
    """

    return worker_speed(worker) <= 5  