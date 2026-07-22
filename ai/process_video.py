import os
import time
import cv2
import tkinter as tk

from tkinter import filedialog

from ai.config import (
    OUTPUT_DIRECTORY,
    VIDEO_PROCESS_EVERY_N_FRAMES
)
from ai.detector import detect
from ai.ppe_checker import count_workers, analyze_ppe
from ai.visualizer import draw_detection_dashboard


def select_video():
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


def process_video(video_path=None):

    if not video_path:
        video_path = select_video()

    if not video_path:
        print("No video selected.")
        return

    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        print("Unable to open the selected video.")
        return

    original_fps = capture.get(cv2.CAP_PROP_FPS)

    if original_fps <= 0:
        original_fps = 25.0

    width = int(
        capture.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    total_frames = int(
        capture.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    os.makedirs(
        OUTPUT_DIRECTORY,
        exist_ok=True
    )

    video_name = os.path.splitext(
        os.path.basename(video_path)
    )[0]

    output_path = os.path.join(
        OUTPUT_DIRECTORY,
        f"{video_name}_detected.mp4"
    )

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        original_fps,
        (width, height)
    )

    if not writer.isOpened():
        capture.release()
        print("Unable to create output video.")
        return

    frame_number = 0
    start_time = time.perf_counter()

    cached_person_results = None
    cached_ppe_results = None
    cached_worker_count = 0
    cached_ppe_summary = {}

    print("Video detection started.")
    print("Press Q to stop.")
    print(
        f"AI processes one frame for every "
        f"{VIDEO_PROCESS_EVERY_N_FRAMES} frames."
    )

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

        elapsed = time.perf_counter() - start_time

        processing_fps = (
            frame_number / elapsed
            if elapsed > 0
            else 0.0
        )

        output_frame = draw_detection_dashboard(
            image=frame,
            person_results=cached_person_results,
            ppe_results=cached_ppe_results,
            worker_count=cached_worker_count,
            ppe_summary=cached_ppe_summary,
            fps=processing_fps,
            show_status_bar=True
        )

        writer.write(output_frame)

        display_frame = output_frame

        if width > 1100:
            display_width = 1100
            display_height = int(
                height * display_width / width
            )

            display_frame = cv2.resize(
                output_frame,
                (display_width, display_height)
            )

        cv2.imshow(
            "Thiran Vision AI - Video Detection",
            display_frame
        )

        if total_frames > 0:
            progress = (
                frame_number / total_frames
            ) * 100

            print(
                f"\rProcessing: {progress:.1f}% "
                f"({frame_number}/{total_frames})",
                end=""
            )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("\nVideo processing stopped.")
            break

    capture.release()
    writer.release()
    cv2.destroyAllWindows()

    total_time = time.perf_counter() - start_time

    print()
    print("Video processing completed.")
    print(f"Processing time: {total_time:.1f} seconds")
    print(f"Output saved: {output_path}")


if __name__ == "__main__":
    process_video()