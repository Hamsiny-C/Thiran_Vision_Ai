import os
import cv2
import tkinter as tk

from tkinter import filedialog

from ai.config import OUTPUT_DIRECTORY
from ai.detector import detect
from ai.ppe_checker import (
    count_workers,
    analyze_ppe
)

# Image uses its own visualizer.
# Video and camera continue using ai.visualizer.
from ai.image_visualizer import (
    draw_detection_dashboard
)


WINDOW_NAME = "Thiran Vision AI - Image Detection"


def select_image():
    root = tk.Tk()
    root.withdraw()

    root.attributes(
        "-topmost",
        True
    )

    image_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[
            (
                "Image files",
                "*.jpg *.jpeg *.png *.bmp *.webp"
            )
        ]
    )

    root.destroy()

    return image_path


def create_preview(
    image,
    maximum_width=1450,
    maximum_height=800
):
    """
    Resize only the preview shown on screen.
    The saved output image is not resized.
    """

    image_height, image_width = image.shape[:2]

    scale = min(
        maximum_width / image_width,
        maximum_height / image_height,
        1.0
    )

    if scale >= 1.0:
        return image.copy()

    preview_width = max(
        1,
        int(image_width * scale)
    )

    preview_height = max(
        1,
        int(image_height * scale)
    )

    return cv2.resize(
        image,
        (
            preview_width,
            preview_height
        ),
        interpolation=cv2.INTER_AREA
    )


def save_image(output_path, image):
    extension = os.path.splitext(
        output_path
    )[1].lower()

    if extension in {
        ".jpg",
        ".jpeg"
    }:
        return cv2.imwrite(
            output_path,
            image,
            [
                cv2.IMWRITE_JPEG_QUALITY,
                100
            ]
        )

    if extension == ".png":
        return cv2.imwrite(
            output_path,
            image,
            [
                cv2.IMWRITE_PNG_COMPRESSION,
                2
            ]
        )

    return cv2.imwrite(
        output_path,
        image
    )


def process_image(image_path=None):
    if not image_path:
        image_path = select_image()

    if not image_path:
        print("No image selected.")
        return

    original_image = cv2.imread(
        image_path,
        cv2.IMREAD_COLOR
    )

    if original_image is None:
        print(
            "Unable to read the selected image."
        )
        return

    print(
        "Detecting workers and PPE..."
    )

    person_results, ppe_results = detect(
        original_image,
        mode="image"
    )

    worker_count = count_workers(
        person_results
    )

    ppe_summary = analyze_ppe(
        ppe_results
    )

    output_image = draw_detection_dashboard(
        image=original_image,
        person_results=person_results,
        ppe_results=ppe_results,
        worker_count=worker_count,
        ppe_summary=ppe_summary,
        show_status_bar=True
    )

    os.makedirs(
        OUTPUT_DIRECTORY,
        exist_ok=True
    )

    original_name = os.path.basename(
        image_path
    )

    name, _ = os.path.splitext(
        original_name
    )

    # Save as PNG to avoid JPEG quality loss.
    output_path = os.path.join(
        OUTPUT_DIRECTORY,
        f"{name}_detected.png"
    )

    saved = save_image(
        output_path,
        output_image
    )

    if not saved:
        print(
            "Unable to save the output image."
        )
        return

    print(
        f"Workers detected: {worker_count}"
    )

    print(
        f"Original image resolution: "
        f"{original_image.shape[1]} x "
        f"{original_image.shape[0]}"
    )

    print(
        f"Output saved: {output_path}"
    )

    preview = create_preview(
        output_image
    )

    cv2.namedWindow(
        WINDOW_NAME,
        cv2.WINDOW_NORMAL
    )

    cv2.imshow(
        WINDOW_NAME,
        preview
    )

    print(
        "Press Q, Esc, or any key to close."
    )

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    process_image() 