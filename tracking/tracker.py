from typing import Dict, List, Tuple

from tracking.centroid_tracker import CentroidTracker


BoundingBox = Tuple[int, int, int, int]


class WorkerTracker:
    """
    Main tracking manager.

    This class acts as the bridge between
    the AI module and the centroid tracker.
    """

    def __init__(
        self,
        max_disappeared: int = 25,
        max_distance: int = 100
    ):

        self.tracker = CentroidTracker(
            max_disappeared=max_disappeared,
            max_distance=max_distance
        )

    def update(
        self,
        person_boxes: List[BoundingBox]
    ) -> Dict[int, Dict]:
        """
        Update worker tracking.

        Parameters
        ----------
        person_boxes

        Example:
        [
            (10,20,100,250),
            (250,40,380,300)
        ]

        Returns
        -------
        Dictionary containing tracked workers.
        """

        return self.tracker.update(person_boxes)

    def get_workers(self) -> Dict[int, Dict]:
        """
        Return every tracked worker.
        """

        return self.tracker.workers

    def get_visible_workers(self) -> Dict[int, Dict]:
        """
        Return only workers visible
        in the current frame.
        """

        return self.tracker.get_visible_workers()

    def worker_count(self) -> int:
        """
        Number of tracked workers.
        """

        return len(self.tracker.workers)

    def reset(self):
        """
        Clear tracker.
        """

        self.tracker.reset()


_global_tracker = WorkerTracker()


def update_tracking(
    person_boxes: List[BoundingBox]
):
    """
    Global helper.

    Used directly by AI.

    Example:

    tracked_workers = update_tracking(boxes)
    """

    return _global_tracker.update(person_boxes)


def get_visible_workers():
    """
    Return visible workers.
    """

    return _global_tracker.get_visible_workers()


def reset_tracker():
    """
    Reset global tracker.
    """

    _global_tracker.reset()  