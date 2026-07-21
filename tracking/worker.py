import time


class Worker:
    """
    Stores information about one tracked worker.
    """

    def __init__(self, worker_id, center):
        self.id = worker_id

        # Current center position
        self.center = center

        # Previous center position
        self.previous_center = center

        # Track history
        self.path = [center]

        # Missing frame count
        self.missing_frames = 0

        # Worker first seen
        self.first_seen = time.time()

        # Last update time
        self.last_seen = time.time()

        # Idle timer
        self.idle_start = None

        # Flags
        self.is_idle = False
        self.in_restricted_zone = False

    def update(self, center):
        """
        Update worker position.
        """

        self.previous_center = self.center
        self.center = center

        self.path.append(center)

        self.last_seen = time.time()

        self.missing_frames = 0

    def increase_missing(self):
        """
        Increase missing frame counter.
        """

        self.missing_frames += 1

    def movement_distance(self):
        """
        Calculate movement distance.
        """

        x1, y1 = self.previous_center
        x2, y2 = self.center

        return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

    def update_idle(self, threshold=5):
        """
        Detect idle worker.
        """

        movement = self.movement_distance()

        if movement < 5:

            if self.idle_start is None:
                self.idle_start = time.time()

            idle_time = time.time() - self.idle_start

            if idle_time >= threshold:
                self.is_idle = True

        else:

            self.idle_start = None
            self.is_idle = False

    def __str__(self):

        return (
            f"Worker("
            f"id={self.id}, "
            f"center={self.center}, "
            f"idle={self.is_idle}, "
            f"missing={self.missing_frames})"
        ) 