import math

from tracking.worker import Worker
from tracking.config import (
    MAX_TRACKING_DISTANCE,
    MAX_MISSING_FRAMES
)


class Tracker:

    def __init__(self):

        self.workers = {}

        self.next_worker_id = 1

    def distance(self, point1, point2):

        return math.sqrt(
            (point1[0] - point2[0]) ** 2 +
            (point1[1] - point2[1]) ** 2
        )

    def update(self, detections):
        """
        detections = list of center points

        Example:
        [(120,230),(420,300)]
        """

        updated = []

        # Match detections with existing workers
        for center in detections:

            matched = None
            minimum_distance = float("inf")

            for worker in self.workers.values():

                d = self.distance(
                    worker.center,
                    center
                )

                if (
                    d < minimum_distance and
                    d < MAX_TRACKING_DISTANCE
                ):
                    minimum_distance = d
                    matched = worker

            if matched:

                matched.update(center)

                updated.append(
                    matched.id
                )

            else:

                worker = Worker(
                    self.next_worker_id,
                    center
                )

                self.workers[
                    self.next_worker_id
                ] = worker

                updated.append(
                    self.next_worker_id
                )

                self.next_worker_id += 1

        # Increase missing frame count
        remove = []

        for worker_id, worker in self.workers.items():

            if worker_id not in updated:

                worker.increase_missing()

                if (
                    worker.missing_frames >
                    MAX_MISSING_FRAMES
                ):
                    remove.append(
                        worker_id
                    )

        # Remove disappeared workers
        for worker_id in remove:

            del self.workers[
                worker_id
            ]

        return self.workers  