import time
from typing import Dict

import cv2
import numpy as np

from tracking.zone_config import (
    get_enabled_zones,
    DANGER_WORKER_COLOR,
    SAFE_WORKER_COLOR,
)

from tracking.alarm import alarm
from tracking.alert import voice_alert

class ZoneMonitor:
    """
    Monitors workers entering restricted zones.
    """

    def __init__(self):
        self.worker_status = {}
        self.worker_entry_time = {}
        self.announced_workers = set()

    @staticmethod
    def point_inside_polygon(point, polygon):
        """
        Check whether a point is inside a polygon.
        """

        if len(polygon) < 3:
            return False

        polygon = np.array(
            polygon,
            dtype=np.int32
        )

        result = cv2.pointPolygonTest(
            polygon,
            point,
            False
        )

        return result >= 0

    def update(self, tracked_workers: Dict):
        """
        Check every tracked worker.
        """

        zones = get_enabled_zones()

        results = {}

        current_time = time.time()

        for worker_id, worker in tracked_workers.items():

            centroid = worker["centroid"]

            inside_zone = False
            zone_name = None

            for _, zone in zones.items():

                if self.point_inside_polygon(
                    centroid,
                    zone["points"]
                ):

                    inside_zone = True
                    zone_name = zone["name"]
                    break

            # ----------------------------
            # Worker entered restricted area
            # ----------------------------
            if inside_zone:

                if worker_id not in self.worker_entry_time:
                    self.worker_entry_time[worker_id] = current_time

                if worker_id not in self.announced_workers:

                    alarm.play_alarm()

                    voice_alert.speak(
                        f"Warning! Worker {worker_id} is in the restricted zone."
                    )
                    
                    self.announced_workers.add(worker_id)
            
            else:

                self.worker_entry_time.pop(worker_id, None)

                self.announced_workers.discard(worker_id)

            results[worker_id] = {

                "worker_id": worker_id,

                "inside_zone": inside_zone,

                "zone_name": zone_name,

                "duration": (
                    current_time
                    - self.worker_entry_time.get(
                        worker_id,
                        current_time
                    )
                ),

                "box": worker["box"],

                "centroid": centroid,

                "trajectory": worker.get(
                    "trajectory",
                    []
                ),

                "color": (
                    DANGER_WORKER_COLOR
                    if inside_zone
                    else SAFE_WORKER_COLOR
                )
            }

        self.worker_status = results

        return results

    def get_worker_status(self, worker_id):

        return self.worker_status.get(worker_id)

    def get_zone_workers(self):
        """
        Return workers currently inside restricted zones.
        """

        return {

            worker_id: worker

            for worker_id, worker
            in self.worker_status.items()

            if worker["inside_zone"]
        }

    def clear(self):

        self.worker_status.clear()

        self.worker_entry_time.clear()

        self.announced_workers.clear()