import os
import cv2
import tkinter as tk

from tkinter import filedialog

from ai.detector import detect
from ai.ppe_checker import count_workers, analyze_ppe
from ai.visualizer import draw_detection_dashboard


def select_video():
    root = tk.Tk()

    root.withdraw()

    video_path = filedialog.askopenfilename(
        title="Select a video for PPE detection",
        filetypes=[
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
            ("MP4 files", "*.mp4"),
            ("AVI files", "*.avi"),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    return video_path


def open_video(video_path):
    if not video_path:
        return None

    if not os.path.exists(video_path):
        print("Error: Selected video does not exist.")
        return None

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        print("Error: Selected video could not be opened.")
        return None

    return video


def process_video(video_path):
    video = open_video(video_path)

    if video is None:
        return {
            "success": False,
            "message": "Video could not be opened."
        }

    width = int(
        video.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    height = int(
        video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    fps = video.get(
        cv2.CAP_PROP_FPS
    )

    total_frames = int(
        video.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    if width <= 0 or height <= 0:
        video.release()

        return {
            "success": False,
            "message": "Invalid video resolution."
        }

    if fps <= 0:
        fps = 25

    output_folder = "ai/output"

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    original_name = os.path.basename(
        video_path
    )

    video_name = os.path.splitext(
        original_name
    )[0]

    output_path = os.path.join(
        output_folder,
        video_name + "_detected.mp4"
    )

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )

    if not writer.isOpened():
        video.release()

        return {
            "success": False,
            "message": "Processed video could not be created."
        }

    frame_count = 0
    maximum_worker_count = 0
    last_ppe_summary = {}

    print("\nTHIRAN VISION AI")
    print("Video selected:", video_path)
    print("Output path:", output_path)
    print("Total frames:", total_frames)
    print("Processing started...\n")

    while True:
        success, frame = video.read()

        if not success:
            break

        person_results, ppe_results = detect(
            frame
        )

        worker_count = count_workers(
            person_results
        )

        ppe_summary = analyze_ppe(
            ppe_results
        )

        maximum_worker_count = max(
            maximum_worker_count,
            worker_count
        )

        last_ppe_summary = ppe_summary

        processed_frame = draw_detection_dashboard(
            image=frame,
            person_results=person_results,
            ppe_results=ppe_results,
            worker_count=worker_count,
            ppe_summary=ppe_summary
        )

        writer.write(
            processed_frame
        )

        frame_count += 1

        if total_frames > 0:
            progress = (
                frame_count / total_frames
            ) * 100

            print(
                f"Processing: "
                f"{frame_count}/{total_frames} "
                f"frames - {progress:.1f}%",
                end="\r"
            )

        else:
            print(
                f"Processing frame: {frame_count}",
                end="\r"
            )

    video.release()
    writer.release()

    print("\n\nVideo processing completed.")
    print("Processed video saved at:")
    print(output_path)

    return {
        "success": True,
        "input_path": video_path,
        "output_path": output_path,
        "frames_processed": frame_count,
        "maximum_worker_count": maximum_worker_count,
        "ppe_summary": last_ppe_summary
    }


if __name__ == "__main__":
    selected_video = select_video()

    if not selected_video:
        print("No video selected.")

    else:
        result = process_video(
            selected_video
        )

        print("\nFinal result:")
        print(result)