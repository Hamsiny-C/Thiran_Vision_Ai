import os
import time
from typing import Dict, List, Tuple

import cv2
import numpy as np
import tkinter as tk

from tkinter import filedialog

from ai.config import (
    OUTPUT_DIRECTORY,
    VIDEO_PROCESS_EVERY_N_FRAMES
)
from ai.detector import detect
from ai.ppe_checker import count_workers, analyze_ppe
from ai.visualizer import draw_detection_dashboard

from tracking.tracker import WorkerTracker
from tracking.zone_monitor import ZoneMonitor
from tracking.zone_config import (
    get_enabled_zones,
    SHOW_ZONE,
    SHOW_ZONE_NAME,
    SHOW_ZONE_ALERT,
    SHOW_TRAJECTORY,
    MAX_TRAJECTORY_POINTS,
    ZONE_BORDER_COLOR,
    ZONE_FILL_COLOR,
    ZONE_TEXT_COLOR,
    ZONE_BORDER_THICKNESS,
    ZONE_FILL_OPACITY,
    WORKER_BOX_THICKNESS,
    TRAJECTORY_COLOR,
    TRAJECTORY_THICKNESS,
    SAFE_WORKER_COLOR,
    DANGER_WORKER_COLOR
)


BoundingBox = Tuple[int, int, int, int]


# ==========================================================
# VIDEO SELECTION
# ==========================================================

def select_video() -> str:
    """
    Open a file-selection window and return the selected
    video path.
    """

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    video_path = filedialog.askopenfilename(
        title="Select a video",
        filetypes=[
            (
                "Video files",
                "*.mp4 *.avi *.mov *.mkv *.wmv"
            )
        ]
    )

    root.destroy()

    return video_path


# ==========================================================
# PERSON BOUNDING-BOX EXTRACTION
# ==========================================================

def extract_person_boxes(person_results) -> List[BoundingBox]:
    """
    Convert YOLO person detections into bounding boxes.

    Output format:
    [
        (x1, y1, x2, y2),
        ...
    ]
    """

    person_boxes: List[BoundingBox] = []

    if person_results is None:
        return person_boxes

    # Ultralytics normally returns a list of Results objects.
    if isinstance(person_results, (list, tuple)):
        results_list = person_results
    else:
        results_list = [person_results]

    for result in results_list:

        if result is None:
            continue

        boxes = getattr(result, "boxes", None)

        if boxes is None:
            continue

        xyxy = getattr(boxes, "xyxy", None)

        if xyxy is None:
            continue

        try:
            coordinates = xyxy.cpu().numpy()
        except AttributeError:
            coordinates = np.asarray(xyxy)

        for coordinate in coordinates:

            if len(coordinate) < 4:
                continue

            x1, y1, x2, y2 = map(
                int,
                coordinate[:4]
            )

            if x2 <= x1 or y2 <= y1:
                continue

            person_boxes.append(
                (x1, y1, x2, y2)
            )

    return person_boxes


# ==========================================================
# TEXT DRAWING
# ==========================================================

def draw_text_with_background(
    frame,
    text: str,
    position: Tuple[int, int],
    text_color=(255, 255, 255),
    background_color=(0, 0, 0),
    font_scale: float = 0.55,
    thickness: int = 2,
    padding: int = 5
):
    """
    Draw readable text with a filled background.
    """

    x, y = position

    font = cv2.FONT_HERSHEY_SIMPLEX

    text_size, baseline = cv2.getTextSize(
        text,
        font,
        font_scale,
        thickness
    )

    text_width, text_height = text_size

    top_left = (
        max(0, x),
        max(0, y - text_height - padding * 2)
    )

    bottom_right = (
        min(frame.shape[1] - 1, x + text_width + padding * 2),
        min(frame.shape[0] - 1, y + baseline)
    )

    cv2.rectangle(
        frame,
        top_left,
        bottom_right,
        background_color,
        -1
    )

    cv2.putText(
        frame,
        text,
        (x + padding, y - padding),
        font,
        font_scale,
        text_color,
        thickness,
        cv2.LINE_AA
    )


# ==========================================================
# RESTRICTED-ZONE DRAWING
# ==========================================================

def draw_restricted_zones(frame):
    """
    Draw all enabled restricted-zone polygons.
    """

    if not SHOW_ZONE:
        return frame

    zones = get_enabled_zones()

    if not zones:
        return frame

    overlay = frame.copy()

    for zone in zones.values():

        points = zone.get("points", [])

        if len(points) < 3:
            continue

        polygon = np.array(
            points,
            dtype=np.int32
        ).reshape((-1, 1, 2))

        cv2.fillPoly(
            overlay,
            [polygon],
            ZONE_FILL_COLOR
        )

    cv2.addWeighted(
        overlay,
        ZONE_FILL_OPACITY,
        frame,
        1.0 - ZONE_FILL_OPACITY,
        0,
        frame
    )

    for zone in zones.values():

        points = zone.get("points", [])

        if len(points) < 3:
            continue

        polygon = np.array(
            points,
            dtype=np.int32
        ).reshape((-1, 1, 2))

        cv2.polylines(
            frame,
            [polygon],
            True,
            ZONE_BORDER_COLOR,
            ZONE_BORDER_THICKNESS,
            cv2.LINE_AA
        )

        if SHOW_ZONE_NAME:

            zone_name = zone.get(
                "name",
                "RESTRICTED ZONE"
            )

            label_x = min(
                point[0]
                for point in points
            )

            label_y = min(
                point[1]
                for point in points
            )

            label_y = max(
                30,
                label_y
            )

            draw_text_with_background(
                frame=frame,
                text=zone_name,
                position=(label_x, label_y),
                text_color=ZONE_TEXT_COLOR,
                background_color=ZONE_BORDER_COLOR,
                font_scale=0.65,
                thickness=2
            )

    return frame


# ==========================================================
# TRAJECTORY DRAWING
# ==========================================================

def draw_worker_trajectory(
    frame,
    trajectory
):
    """
    Draw the recent movement path of one worker.
    """

    if not SHOW_TRAJECTORY:
        return

    if not trajectory or len(trajectory) < 2:
        return

    recent_points = trajectory[
        -MAX_TRAJECTORY_POINTS:
    ]

    for index in range(
        1,
        len(recent_points)
    ):

        previous_point = tuple(
            map(
                int,
                recent_points[index - 1]
            )
        )

        current_point = tuple(
            map(
                int,
                recent_points[index]
            )
        )

        cv2.line(
            frame,
            previous_point,
            current_point,
            TRAJECTORY_COLOR,
            TRAJECTORY_THICKNESS,
            cv2.LINE_AA
        )


# ==========================================================
# TRACKED-WORKER DRAWING
# ==========================================================

def draw_tracked_workers(
    frame,
    zone_results: Dict
):
    """
    Draw worker IDs, tracking boxes, centroids,
    trajectories, and restricted-zone status.
    """

    for worker_id, worker in zone_results.items():

        box = worker.get("box")
        centroid = worker.get("centroid")
        trajectory = worker.get(
            "trajectory",
            []
        )

        inside_zone = worker.get(
            "inside_zone",
            False
        )

        zone_name = worker.get(
            "zone_name"
        )

        duration = worker.get(
            "duration",
            0.0
        )

        color = (
            DANGER_WORKER_COLOR
            if inside_zone
            else SAFE_WORKER_COLOR
        )

        draw_worker_trajectory(
            frame,
            trajectory
        )

        if box is not None:

            x1, y1, x2, y2 = map(
                int,
                box
            )

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                color,
                WORKER_BOX_THICKNESS,
                cv2.LINE_AA
            )

            worker_label = (
                f"Worker {worker_id}"
            )

            if inside_zone:
                worker_label += " - RESTRICTED"

            draw_text_with_background(
                frame=frame,
                text=worker_label,
                position=(
                    x1,
                    max(25, y1)
                ),
                text_color=(255, 255, 255),
                background_color=color,
                font_scale=0.55,
                thickness=2
            )

        if centroid is not None:

            center_x, center_y = map(
                int,
                centroid
            )

            cv2.circle(
                frame,
                (center_x, center_y),
                5,
                color,
                -1,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                str(worker_id),
                (center_x + 8, center_y - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
                cv2.LINE_AA
            )

        if inside_zone and SHOW_ZONE_ALERT:

            alert_text = (
                f"ALERT: Worker {worker_id} entered "
                f"{zone_name or 'restricted zone'} "
                f"({duration:.1f}s)"
            )

            worker["alert_text"] = alert_text

    return frame


# ==========================================================
# ALERT PANEL
# ==========================================================

def draw_alert_panel(
    frame,
    zone_results: Dict
):
    """
    Display active restricted-zone alerts.
    """

    if not SHOW_ZONE_ALERT:
        return frame

    active_alerts = []

    for worker_id, worker in zone_results.items():

        if not worker.get(
            "inside_zone",
            False
        ):
            continue

        zone_name = worker.get(
            "zone_name",
            "RESTRICTED ZONE"
        )

        duration = worker.get(
            "duration",
            0.0
        )

        active_alerts.append(
            f"Worker {worker_id}: "
            f"{zone_name} - {duration:.1f}s"
        )

    if not active_alerts:
        return frame

    panel_x = 15
    panel_y = 75

    panel_width = min(
        frame.shape[1] - 30,
        620
    )

    panel_height = (
        48
        + len(active_alerts) * 34
    )

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (panel_x, panel_y),
        (
            panel_x + panel_width,
            panel_y + panel_height
        ),
        (0, 0, 180),
        -1
    )

    cv2.addWeighted(
        overlay,
        0.82,
        frame,
        0.18,
        0,
        frame
    )

    cv2.rectangle(
        frame,
        (panel_x, panel_y),
        (
            panel_x + panel_width,
            panel_y + panel_height
        ),
        (0, 0, 255),
        2
    )

    cv2.putText(
        frame,
        "RESTRICTED ZONE ALERT",
        (
            panel_x + 12,
            panel_y + 30
        ),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    for index, alert in enumerate(
        active_alerts
    ):

        cv2.putText(
            frame,
            alert,
            (
                panel_x + 12,
                panel_y + 64 + index * 34
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

    return frame


# ==========================================================
# TRACKING SUMMARY
# ==========================================================

def draw_tracking_summary(
    frame,
    tracked_workers: Dict,
    zone_results: Dict
):
    """
    Display worker-tracking counts.
    """

    visible_count = 0

    for worker in tracked_workers.values():

        if worker.get(
            "visible",
            True
        ):
            visible_count += 1

    restricted_count = sum(
        1
        for worker in zone_results.values()
        if worker.get(
            "inside_zone",
            False
        )
    )

    summary_text = (
        f"Tracked: {visible_count} | "
        f"Restricted: {restricted_count}"
    )

    text_size, _ = cv2.getTextSize(
        summary_text,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        2
    )

    text_width = text_size[0]

    x_position = max(
        10,
        frame.shape[1] - text_width - 30
    )

    draw_text_with_background(
        frame=frame,
        text=summary_text,
        position=(x_position, 35),
        text_color=(255, 255, 255),
        background_color=(
            (0, 0, 180)
            if restricted_count > 0
            else (30, 30, 30)
        ),
        font_scale=0.6,
        thickness=2
    )

    return frame


# ==========================================================
# MAIN VIDEO PROCESSING
# ==========================================================

def process_video(video_path=None):

    if not video_path:
        video_path = select_video()

    if not video_path:
        print("No video selected.")
        return

    capture = cv2.VideoCapture(
        video_path
    )

    if not capture.isOpened():
        print(
            "Unable to open the selected video."
        )
        return

    original_fps = capture.get(
        cv2.CAP_PROP_FPS
    )

    if original_fps <= 0:
        original_fps = 25.0

    width = int(
        capture.get(
            cv2.CAP_PROP_FRAME_WIDTH
        )
    )

    height = int(
        capture.get(
            cv2.CAP_PROP_FRAME_HEIGHT
        )
    )

    total_frames = int(
        capture.get(
            cv2.CAP_PROP_FRAME_COUNT
        )
    )

    if width <= 0 or height <= 0:
        capture.release()
        print("Invalid video dimensions.")
        return

    os.makedirs(
        OUTPUT_DIRECTORY,
        exist_ok=True
    )

    video_name = os.path.splitext(
        os.path.basename(video_path)
    )[0]

    output_path = os.path.join(
        OUTPUT_DIRECTORY,
        f"{video_name}_tracked.mp4"
    )

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        original_fps,
        (width, height)
    )

    if not writer.isOpened():
        capture.release()
        print(
            "Unable to create output video."
        )
        return

    # Separate tracker instance for every video.
    worker_tracker = WorkerTracker(
        max_disappeared=max(
            20,
            VIDEO_PROCESS_EVERY_N_FRAMES * 8
        ),
        max_distance=120
    )

    zone_monitor = ZoneMonitor()

    frame_number = 0
    start_time = time.perf_counter()

    cached_person_results = None
    cached_ppe_results = None
    cached_worker_count = 0
    cached_ppe_summary = {}

    tracked_workers: Dict = {}
    zone_results: Dict = {}

    print("Video detection and tracking started.")
    print("Press Q to stop.")

    print(
        f"AI processes one frame for every "
        f"{VIDEO_PROCESS_EVERY_N_FRAMES} frames."
    )

    try:

        while capture.isOpened():

            success, frame = capture.read()

            if not success:
                break

            frame_number += 1

            should_detect = (
                cached_person_results is None
                or frame_number
                % VIDEO_PROCESS_EVERY_N_FRAMES
                == 1
            )

            if should_detect:

                (
                    cached_person_results,
                    cached_ppe_results
                ) = detect(
                    frame,
                    mode="video"
                )

                cached_worker_count = count_workers(
                    cached_person_results
                )

                cached_ppe_summary = analyze_ppe(
                    cached_ppe_results
                )

                person_boxes = extract_person_boxes(
                    cached_person_results
                )

                tracked_workers = (
                    worker_tracker.update(
                        person_boxes
                    )
                )

            if tracked_workers:

                zone_results = zone_monitor.update(
                    tracked_workers
                )

            else:
                zone_results = {}

            elapsed = (
                time.perf_counter()
                - start_time
            )

            processing_fps = (
                frame_number / elapsed
                if elapsed > 0
                else 0.0
            )

            output_frame = (
                draw_detection_dashboard(
                    image=frame,
                    person_results=(
                        cached_person_results
                    ),
                    ppe_results=(
                        cached_ppe_results
                    ),
                    worker_count=(
                        cached_worker_count
                    ),
                    ppe_summary=(
                        cached_ppe_summary
                    ),
                    fps=processing_fps,
                    show_status_bar=True
                )
            )

            # Draw restricted zones first so worker
            # boxes and labels remain clearly visible.
            output_frame = draw_restricted_zones(
                output_frame
            )

            output_frame = draw_tracked_workers(
                output_frame,
                zone_results
            )

            output_frame = draw_alert_panel(
                output_frame,
                zone_results
            )

            output_frame = draw_tracking_summary(
                output_frame,
                tracked_workers,
                zone_results
            )

            writer.write(output_frame)

            display_frame = output_frame

            if width > 1100:

                display_width = 1100

                display_height = int(
                    height
                    * display_width
                    / width
                )

                display_frame = cv2.resize(
                    output_frame,
                    (
                        display_width,
                        display_height
                    ),
                    interpolation=cv2.INTER_AREA
                )

            cv2.imshow(
                "Thiran Vision AI - "
                "Worker Tracking",
                display_frame
            )

            if total_frames > 0:

                progress = (
                    frame_number
                    / total_frames
                ) * 100

                print(
                    f"\rProcessing: "
                    f"{progress:.1f}% "
                    f"({frame_number}/"
                    f"{total_frames})",
                    end="",
                    flush=True
                )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                print(
                    "\nVideo processing stopped."
                )

                break

    except KeyboardInterrupt:

        print(
            "\nVideo processing interrupted."
        )

    except Exception as error:

        print(
            f"\nVideo processing error: "
            f"{error}"
        )

        raise

    finally:

        capture.release()
        writer.release()
        cv2.destroyAllWindows()

        worker_tracker.reset()
        zone_monitor.clear()

    total_time = (
        time.perf_counter()
        - start_time
    )

    print()
    print(
        "Video processing completed."
    )

    print(
        f"Processing time: "
        f"{total_time:.1f} seconds"
    )

    print(
        f"Output saved: {output_path}"
    )


if __name__ == "__main__":
    process_video() 