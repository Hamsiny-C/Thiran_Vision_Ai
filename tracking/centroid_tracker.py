from collections import OrderedDict
from typing import Dict, List, Tuple

import numpy as np


BoundingBox = Tuple[int, int, int, int]
Centroid = Tuple[int, int]


class CentroidTracker:
    """
    Assigns a unique ID to every detected worker and keeps the same ID
    while the worker moves across video frames.
    """

    def __init__(
        self,
        max_disappeared: int = 25,
        max_distance: float = 100.0
    ):
        self.next_worker_id = 1

        self.workers: OrderedDict[int, Dict] = OrderedDict()
        self.disappeared: OrderedDict[int, int] = OrderedDict()

        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    @staticmethod
    def calculate_centroid(box: BoundingBox) -> Centroid:
        """
        Calculate the center point of a bounding box.

        Box format:
        (x1, y1, x2, y2)
        """

        x1, y1, x2, y2 = box

        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        return center_x, center_y

    @staticmethod
    def validate_boxes(
        bounding_boxes: List[BoundingBox]
    ) -> List[BoundingBox]:
        """
        Remove invalid bounding boxes.
        """

        valid_boxes = []

        for box in bounding_boxes:
            if box is None or len(box) != 4:
                continue

            x1, y1, x2, y2 = map(int, box)

            if x2 <= x1 or y2 <= y1:
                continue

            valid_boxes.append((x1, y1, x2, y2))

        return valid_boxes

    def register(
        self,
        box: BoundingBox,
        centroid: Centroid
    ) -> int:
        """
        Register a newly detected worker.
        """

        worker_id = self.next_worker_id

        self.workers[worker_id] = {
            "worker_id": worker_id,
            "box": box,
            "centroid": centroid,
            "previous_centroid": centroid,
            "trajectory": [centroid],
            "visible": True
        }

        self.disappeared[worker_id] = 0
        self.next_worker_id += 1

        return worker_id

    def deregister(self, worker_id: int) -> None:
        """
        Remove a worker who has disappeared for too many frames.
        """

        if worker_id in self.workers:
            del self.workers[worker_id]

        if worker_id in self.disappeared:
            del self.disappeared[worker_id]

    @staticmethod
    def calculate_distance_matrix(
        existing_centroids: List[Centroid],
        detected_centroids: List[Centroid]
    ) -> np.ndarray:
        """
        Calculate distances between tracked workers and new detections.
        """

        old_points = np.array(
            existing_centroids,
            dtype=np.float32
        )

        new_points = np.array(
            detected_centroids,
            dtype=np.float32
        )

        difference = (
            old_points[:, np.newaxis, :]
            - new_points[np.newaxis, :, :]
        )

        distances = np.sqrt(
            np.sum(difference ** 2, axis=2)
        )

        return distances

    def update(
        self,
        bounding_boxes: List[BoundingBox]
    ) -> Dict[int, Dict]:
        """
        Update worker tracking using person bounding boxes.

        Input:
        [
            (x1, y1, x2, y2),
            (x1, y1, x2, y2)
        ]

        Output:
        {
            1: {
                "worker_id": 1,
                "box": (...),
                "centroid": (...),
                "trajectory": [...]
            }
        }
        """

        valid_boxes = self.validate_boxes(bounding_boxes)

        for worker_id in self.workers:
            self.workers[worker_id]["visible"] = False

        # No person detected in the current frame.
        if len(valid_boxes) == 0:
            for worker_id in list(self.disappeared.keys()):
                self.disappeared[worker_id] += 1

                if (
                    self.disappeared[worker_id]
                    > self.max_disappeared
                ):
                    self.deregister(worker_id)

            return dict(self.workers)

        detected_centroids = [
            self.calculate_centroid(box)
            for box in valid_boxes
        ]

        # First video frame or no existing workers.
        if len(self.workers) == 0:
            for box, centroid in zip(
                valid_boxes,
                detected_centroids
            ):
                self.register(box, centroid)

            return dict(self.workers)

        worker_ids = list(self.workers.keys())

        existing_centroids = [
            self.workers[worker_id]["centroid"]
            for worker_id in worker_ids
        ]

        distance_matrix = self.calculate_distance_matrix(
            existing_centroids,
            detected_centroids
        )

        row_order = np.argsort(
            distance_matrix.min(axis=1)
        )

        column_order = np.argmin(
            distance_matrix,
            axis=1
        )[row_order]

        used_rows = set()
        used_columns = set()

        for row, column in zip(
            row_order,
            column_order
        ):
            if row in used_rows:
                continue

            if column in used_columns:
                continue

            distance = distance_matrix[row, column]

            if distance > self.max_distance:
                continue

            worker_id = worker_ids[row]
            old_centroid = self.workers[
                worker_id
            ]["centroid"]

            new_centroid = detected_centroids[column]

            self.workers[worker_id][
                "previous_centroid"
            ] = old_centroid

            self.workers[worker_id][
                "centroid"
            ] = new_centroid

            self.workers[worker_id][
                "box"
            ] = valid_boxes[column]

            self.workers[worker_id][
                "visible"
            ] = True

            self.workers[worker_id][
                "trajectory"
            ].append(new_centroid)

            # Keep only the latest 30 movement points.
            if (
                len(
                    self.workers[worker_id][
                        "trajectory"
                    ]
                )
                > 30
            ):
                self.workers[worker_id][
                    "trajectory"
                ] = self.workers[
                    worker_id
                ]["trajectory"][-30:]

            self.disappeared[worker_id] = 0

            used_rows.add(row)
            used_columns.add(column)

        unused_rows = (
            set(range(distance_matrix.shape[0]))
            - used_rows
        )

        unused_columns = (
            set(range(distance_matrix.shape[1]))
            - used_columns
        )

        # Existing worker was not detected.
        for row in unused_rows:
            worker_id = worker_ids[row]

            self.disappeared[worker_id] += 1

            if (
                self.disappeared[worker_id]
                > self.max_disappeared
            ):
                self.deregister(worker_id)

        # Completely new worker detected.
        for column in unused_columns:
            self.register(
                valid_boxes[column],
                detected_centroids[column]
            )

        return dict(self.workers)

    def get_visible_workers(self) -> Dict[int, Dict]:
        """
        Return only workers visible in the current frame.
        """

        return {
            worker_id: worker_data
            for worker_id, worker_data
            in self.workers.items()
            if worker_data.get("visible", False)
        }

    def reset(self) -> None:
        """
        Reset all tracking information.
        """

        self.next_worker_id = 1
        self.workers.clear()
        self.disappeared.clear()  