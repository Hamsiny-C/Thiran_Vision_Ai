import threading
import time

import cv2

from ai.config import (
    CAMERA_ID,
    PROCESS_EVERY_N_FRAMES,
)
from ai.detector import detect
from ai.ppe_checker import count_workers, analyze_ppe
from ai.visualizer import draw_detection_dashboard


class CameraDetectionApp:
    def __init__(self):
        self.capture = None

        self.latest_frame = None
        self.latest_person_results = None
        self.latest_ppe_results = None
        self.latest_worker_count = 0
        self.latest_ppe_summary = {}

        self.running = False
        self.detection_busy = False

        self.frame_number = 0
        self.smoothed_fps = 0.0
        self.previous_time = time.perf_counter()

        self.lock = threading.Lock()

    def open_camera(self):
        self.capture = cv2.VideoCapture(
            CAMERA_ID,
            cv2.CAP_DSHOW
        )

        if not self.capture.isOpened():
            self.capture = cv2.VideoCapture(CAMERA_ID)

        if not self.capture.isOpened():
            raise RuntimeError("Unable to open the camera.")

        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        self.capture.set(cv2.CAP_PROP_FPS, 30)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def detection_worker(self, frame):
        try:
            person_results, ppe_results = detect(
                frame,
                mode="camera"
            )

            worker_count = count_workers(person_results)
            ppe_summary = analyze_ppe(ppe_results)

            with self.lock:
                self.latest_person_results = person_results
                self.latest_ppe_results = ppe_results
                self.latest_worker_count = worker_count
                self.latest_ppe_summary = ppe_summary

        except Exception as error:
            print(f"Detection error: {error}")

        finally:
            self.detection_busy = False

    def start_detection_thread(self, frame):
        if self.detection_busy:
            return

        self.detection_busy = True

        thread = threading.Thread(
            target=self.detection_worker,
            args=(frame.copy(),),
            daemon=True
        )

        thread.start()

    def calculate_fps(self):
        current_time = time.perf_counter()
        elapsed = current_time - self.previous_time
        self.previous_time = current_time

        current_fps = 1.0 / elapsed if elapsed > 0 else 0.0

        if self.smoothed_fps == 0:
            self.smoothed_fps = current_fps
        else:
            self.smoothed_fps = (
                0.90 * self.smoothed_fps
                + 0.10 * current_fps
            )

    def build_layout(self, frame):
        screen_width = 1366
        screen_height = 768

        panel_width = 320
        video_width = screen_width - panel_width

        resized_frame = cv2.resize(
            frame,
            (video_width, screen_height)
        )

        panel = self.create_side_panel(
            panel_width,
            screen_height
        )

        return cv2.hconcat([
            resized_frame,
            panel
        ])

    def create_side_panel(self, width, height):
        panel = 25 * (
            cv2.UMat(height, width, cv2.CV_8UC3).get()
        )

        title_font = cv2.FONT_HERSHEY_SIMPLEX
        normal_font = cv2.FONT_HERSHEY_SIMPLEX

        with self.lock:
            worker_count = self.latest_worker_count
            summary = self.latest_ppe_summary.copy()

        cv2.putText(
            panel,
            "THIRAN VISION AI",
            (24, 50),
            title_font,
            0.75,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        cv2.line(
            panel,
            (20, 70),
            (width - 20, 70),
            (120, 120, 120),
            1
        )

        cv2.putText(
            panel,
            "LIVE MONITORING",
            (24, 110),
            normal_font,
            0.58,
            (0, 220, 255),
            2,
            cv2.LINE_AA
        )

        items = [
            ("Workers", worker_count),
            ("Hardhat", summary.get("hardhat", 0)),
            ("No Hardhat", summary.get("no_hardhat", 0)),
            ("Safety Vest", summary.get("safety_vest", 0)),
            ("No Vest", summary.get("no_safety_vest", 0)),
            ("Gloves", summary.get("gloves", 0)),
            ("No Gloves", summary.get("no_gloves", 0)),
            ("Falls", summary.get("fall_detected", 0)),
        ]

        y = 165

        for label, value in items:
            cv2.putText(
                panel,
                label,
                (24, y),
                normal_font,
                0.52,
                (210, 210, 210),
                1,
                cv2.LINE_AA
            )

            cv2.putText(
                panel,
                str(value),
                (width - 70, y),
                normal_font,
                0.58,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            y += 48

        cv2.line(
            panel,
            (20, height - 120),
            (width - 20, height - 120),
            (120, 120, 120),
            1
        )

        cv2.putText(
            panel,
            f"Display FPS: {self.smoothed_fps:.1f}",
            (24, height - 75),
            normal_font,
            0.52,
            (0, 255, 150),
            1,
            cv2.LINE_AA
        )

        cv2.putText(
            panel,
            "Press Q to exit",
            (24, height - 35),
            normal_font,
            0.48,
            (180, 180, 180),
            1,
            cv2.LINE_AA
        )

        return panel

    def run(self):
        self.open_camera()
        self.running = True

        window_name = "Thiran Vision AI - Live Safety Monitoring"

        cv2.namedWindow(
            window_name,
            cv2.WINDOW_NORMAL
        )

        cv2.setWindowProperty(
            window_name,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )

        print("Live camera started.")
        print("Press Q to stop.")

        while self.running:
            success, frame = self.capture.read()

            if not success:
                print("Unable to read camera frame.")
                break

            self.frame_number += 1
            self.calculate_fps()

            if (
                self.frame_number % PROCESS_EVERY_N_FRAMES == 0
                and not self.detection_busy
            ):
                self.start_detection_thread(frame)

            with self.lock:
                person_results = self.latest_person_results
                ppe_results = self.latest_ppe_results
                worker_count = self.latest_worker_count
                ppe_summary = self.latest_ppe_summary.copy()

            if person_results is not None:
                displayed_frame = draw_detection_dashboard(
                    image=frame,
                    person_results=person_results,
                    ppe_results=ppe_results,
                    worker_count=worker_count,
                    ppe_summary=ppe_summary,
                    fps=None,
                    show_status_bar=False
                )
            else:
                displayed_frame = frame.copy()

            full_layout = self.build_layout(displayed_frame)

            cv2.imshow(
                window_name,
                full_layout
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                self.running = False

        self.capture.release()
        cv2.destroyAllWindows()


def start_camera():
    app = CameraDetectionApp()
    app.run()


if __name__ == "__main__":
    start_camera()