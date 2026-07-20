import os
import cv2
import tkinter as tk

from tkinter import filedialog

from ai.detector import detect
from ai.ppe_checker import count_workers, analyze_ppe
from ai.visualizer import draw_detection_dashboard


def select_image():
    root = tk.Tk()
    root.withdraw()

    image_path = filedialog.askopenfilename(
        title="Select an image for PPE detection",
        filetypes=[
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.webp"),
            ("JPG files", "*.jpg *.jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
    )

    root.destroy()

    return image_path


def process_image(image_path):
    if not image_path:
        return {
            "success": False,
            "message": "No image selected."
        }

    if not os.path.exists(image_path):
        return {
            "success": False,
            "message": "Selected image does not exist."
        }

    image = cv2.imread(image_path)

    if image is None:
        return {
            "success": False,
            "message": "Image could not be opened."
        }

    output_folder = "ai/output"

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    original_name = os.path.basename(
        image_path
    )

    image_name = os.path.splitext(
        original_name
    )[0]

    output_path = os.path.join(
        output_folder,
        image_name + "_detected.jpg"
    )

    print("\nTHIRAN VISION AI")
    print("Image selected:", image_path)
    print("Detection started...")

    # Detect person and PPE
    person_results, ppe_results = detect(
        image
    )

    # Count detected workers
    worker_count = count_workers(
        person_results
    )

    # Analyze helmet, vest and other PPE
    ppe_summary = analyze_ppe(
        ppe_results
    )

    # Draw worker boxes, PPE status and dashboard
    processed_image = draw_detection_dashboard(
        image=image,
        person_results=person_results,
        ppe_results=ppe_results,
        worker_count=worker_count,
        ppe_summary=ppe_summary
    )

    saved = cv2.imwrite(
        output_path,
        processed_image
    )

    if not saved:
        return {
            "success": False,
            "message": "Processed image could not be saved."
        }

    print("Detection completed.")
    print("Workers detected:", worker_count)
    print("Processed image saved at:", output_path)

    return {
        "success": True,
        "input_path": image_path,
        "output_path": output_path,
        "worker_count": worker_count,
        "ppe_summary": ppe_summary
    }


if __name__ == "__main__":
    print("Program started...")

    selected_image = select_image()

    print("After file dialog:", selected_image)

    if not selected_image:
        print("No image selected.")
    else:
        result = process_image(selected_image)
        print(result)