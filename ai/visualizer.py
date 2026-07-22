import cv2

from ai.ppe_checker import extract_detections


# =========================================================
# PPE CLASS NAMES
# =========================================================

POSITIVE_HELMET_NAMES = {
    "hardhat",
    "helmet"
}

NEGATIVE_HELMET_NAMES = {
    "no-hardhat",
    "no-helmet"
}

POSITIVE_VEST_NAMES = {
    "safety-vest",
    "vest"
}

NEGATIVE_VEST_NAMES = {
    "no-safety-vest",
    "no-vest"
}

POSITIVE_GLOVE_NAMES = {
    "gloves",
    "glove"
}

NEGATIVE_GLOVE_NAMES = {
    "no-gloves",
    "no-glove"
}

FALL_NAMES = {
    "fall",
    "fall-detected"
}


# =========================================================
# BOX UTILITY FUNCTIONS
# =========================================================

def clamp_box(box, image_width, image_height):
    """
    Keeps bounding-box coordinates inside the image.
    """

    x1, y1, x2, y2 = box

    x1 = max(0, min(int(x1), image_width - 1))
    y1 = max(0, min(int(y1), image_height - 1))
    x2 = max(0, min(int(x2), image_width - 1))
    y2 = max(0, min(int(y2), image_height - 1))

    return x1, y1, x2, y2


def box_center(box):
    x1, y1, x2, y2 = box

    center_x = int((x1 + x2) / 2)
    center_y = int((y1 + y2) / 2)

    return center_x, center_y


def point_inside_box(point, box):
    point_x, point_y = point
    x1, y1, x2, y2 = box

    return (
        x1 <= point_x <= x2
        and y1 <= point_y <= y2
    )


def intersection_over_item_area(person_box, item_box):
    px1, py1, px2, py2 = person_box
    ix1, iy1, ix2, iy2 = item_box

    intersection_x1 = max(px1, ix1)
    intersection_y1 = max(py1, iy1)
    intersection_x2 = min(px2, ix2)
    intersection_y2 = min(py2, iy2)

    intersection_width = max(
        0,
        intersection_x2 - intersection_x1
    )

    intersection_height = max(
        0,
        intersection_y2 - intersection_y1
    )

    intersection_area = (
        intersection_width
        * intersection_height
    )

    item_width = max(1, ix2 - ix1)
    item_height = max(1, iy2 - iy1)

    item_area = item_width * item_height

    return intersection_area / item_area


def belongs_to_worker(person_box, ppe_box):
    """
    Checks whether a PPE detection belongs to a worker.
    """

    ppe_center = box_center(ppe_box)

    if point_inside_box(ppe_center, person_box):
        return True

    overlap = intersection_over_item_area(
        person_box,
        ppe_box
    )

    return overlap >= 0.50


# =========================================================
# PPE STATUS FUNCTIONS
# =========================================================

def choose_status(
    current_value,
    current_confidence,
    new_value,
    new_confidence
):
    if new_confidence > current_confidence:
        return new_value, new_confidence

    return current_value, current_confidence


def get_worker_ppe_status(
    person_box,
    ppe_detections
):
    status = {
        "helmet": None,
        "vest": None,
        "gloves": None,
        "fall": False
    }

    confidence = {
        "helmet": 0.0,
        "vest": 0.0,
        "gloves": 0.0
    }

    for detection in ppe_detections:

        ppe_box = detection.get("box")

        if ppe_box is None:
            continue

        if not belongs_to_worker(
            person_box,
            ppe_box
        ):
            continue

        name = detection.get(
            "normalized_name",
            ""
        )

        score = float(
            detection.get(
                "confidence",
                0.0
            )
        )

        if name in POSITIVE_HELMET_NAMES:
            (
                status["helmet"],
                confidence["helmet"]
            ) = choose_status(
                status["helmet"],
                confidence["helmet"],
                True,
                score
            )

        elif name in NEGATIVE_HELMET_NAMES:
            (
                status["helmet"],
                confidence["helmet"]
            ) = choose_status(
                status["helmet"],
                confidence["helmet"],
                False,
                score
            )

        elif name in POSITIVE_VEST_NAMES:
            (
                status["vest"],
                confidence["vest"]
            ) = choose_status(
                status["vest"],
                confidence["vest"],
                True,
                score
            )

        elif name in NEGATIVE_VEST_NAMES:
            (
                status["vest"],
                confidence["vest"]
            ) = choose_status(
                status["vest"],
                confidence["vest"],
                False,
                score
            )

        elif name in POSITIVE_GLOVE_NAMES:
            (
                status["gloves"],
                confidence["gloves"]
            ) = choose_status(
                status["gloves"],
                confidence["gloves"],
                True,
                score
            )

        elif name in NEGATIVE_GLOVE_NAMES:
            (
                status["gloves"],
                confidence["gloves"]
            ) = choose_status(
                status["gloves"],
                confidence["gloves"],
                False,
                score
            )

        elif name in FALL_NAMES:
            status["fall"] = True

    return status


def status_word(value):
    if value is True:
        return "YES"

    if value is False:
        return "NO"

    return "N/A"


def worker_is_unsafe(status):
    """
    Worker is unsafe only when the model detects a negative PPE
    class or a fall.
    """

    return (
        status["helmet"] is False
        or status["vest"] is False
        or status["gloves"] is False
        or status["fall"] is True
    )


# =========================================================
# DRAWING FUNCTIONS
# =========================================================

def get_scaled_values(image):
    """
    Creates suitable text and line sizes based on image resolution.
    The image itself is never resized.
    """

    image_height, image_width = image.shape[:2]

    reference_size = max(
        image_width,
        image_height
    )

    font_scale = max(
        0.42,
        min(reference_size / 2200, 0.65)
    )

    small_font_scale = max(
        0.36,
        min(reference_size / 2600, 0.52)
    )

    box_thickness = max(
        1,
        min(int(reference_size / 700), 3)
    )

    text_thickness = 1

    return (
        font_scale,
        small_font_scale,
        box_thickness,
        text_thickness
    )


def draw_compact_label(
    frame,
    text,
    x,
    y,
    background_color,
    font_scale,
    text_thickness=1
):
    """
    Draws a small readable label without covering large
    parts of the image.
    """

    font = cv2.FONT_HERSHEY_SIMPLEX
    padding_x = 6
    padding_y = 5

    text_size, baseline = cv2.getTextSize(
        text,
        font,
        font_scale,
        text_thickness
    )

    text_width, text_height = text_size

    image_height, image_width = frame.shape[:2]

    label_width = (
        text_width
        + padding_x * 2
    )

    label_height = (
        text_height
        + padding_y * 2
        + baseline
    )

    x = max(
        0,
        min(
            int(x),
            image_width - label_width
        )
    )

    y = int(y)

    if y - label_height < 0:
        top = max(0, y)
        bottom = min(
            image_height - 1,
            top + label_height
        )
    else:
        bottom = min(
            image_height - 1,
            y
        )

        top = max(
            0,
            bottom - label_height
        )

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (x, top),
        (x + label_width, bottom),
        background_color,
        -1
    )

    cv2.addWeighted(
        overlay,
        0.78,
        frame,
        0.22,
        0,
        frame
    )

    cv2.rectangle(
        frame,
        (x, top),
        (x + label_width, bottom),
        background_color,
        1
    )

    text_y = (
        top
        + padding_y
        + text_height
    )

    cv2.putText(
        frame,
        text,
        (
            x + padding_x,
            text_y
        ),
        font,
        font_scale,
        (255, 255, 255),
        text_thickness,
        cv2.LINE_AA
    )


def draw_status_bar(
    frame,
    worker_count,
    safe_count,
    unsafe_count,
    fps=None
):
    """
    Draws a small top status bar.
    It does not resize or reduce the image quality.
    """

    image_height, image_width = frame.shape[:2]

    (
        font_scale,
        _,
        _,
        text_thickness
    ) = get_scaled_values(frame)

    bar_height = max(
        38,
        int(image_height * 0.055)
    )

    bar_height = min(
        bar_height,
        58
    )

    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (0, 0),
        (image_width, bar_height),
        (18, 18, 18),
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

    title = "THIRAN VISION AI"

    status_text = (
        f"Workers: {worker_count}   "
        f"Safe: {safe_count}   "
        f"Unsafe: {unsafe_count}"
    )

    title_x = 14

    text_y = int(
        bar_height * 0.68
    )

    cv2.putText(
        frame,
        title,
        (title_x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (255, 255, 255),
        text_thickness,
        cv2.LINE_AA
    )

    title_width = cv2.getTextSize(
        title,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        text_thickness
    )[0][0]

    status_x = title_x + title_width + 30

    status_width = cv2.getTextSize(
        status_text,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        text_thickness
    )[0][0]

    available_width = image_width - status_x - 15

    if status_width <= available_width:
        cv2.putText(
            frame,
            status_text,
            (status_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (220, 220, 220),
            text_thickness,
            cv2.LINE_AA
        )
    else:
        compact_status = (
            f"W:{worker_count}  "
            f"S:{safe_count}  "
            f"U:{unsafe_count}"
        )

        cv2.putText(
            frame,
            compact_status,
            (status_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (220, 220, 220),
            text_thickness,
            cv2.LINE_AA
        )

    if fps is not None:
        fps_text = f"FPS {fps:.1f}"

        fps_width = cv2.getTextSize(
            fps_text,
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            text_thickness
        )[0][0]

        fps_x = max(
            10,
            image_width - fps_width - 15
        )

        cv2.putText(
            frame,
            fps_text,
            (fps_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (0, 255, 255),
            text_thickness,
            cv2.LINE_AA
        )


def draw_fall_alert(
    frame,
    x1,
    y2,
    font_scale
):
    text = "FALL DETECTED"

    image_height = frame.shape[0]

    alert_y = min(
        image_height - 5,
        y2 + 28
    )

    draw_compact_label(
        frame=frame,
        text=text,
        x=x1,
        y=alert_y,
        background_color=(0, 0, 220),
        font_scale=font_scale,
        text_thickness=1
    )


# =========================================================
# MAIN VISUALIZER FUNCTION
# =========================================================

def draw_detection_dashboard(
    image,
    person_results,
    ppe_results,
    worker_count=None,
    ppe_summary=None,
    fps=None,
    show_status_bar=True
):
    """
    Draws clean worker bounding boxes without resizing
    or lowering the original image quality.
    """

    if image is None:
        raise ValueError(
            "Input image cannot be None."
        )

    # Work on a copy of the original-resolution image.
    output_frame = image.copy()

    image_height, image_width = output_frame.shape[:2]

    (
        font_scale,
        small_font_scale,
        box_thickness,
        text_thickness
    ) = get_scaled_values(output_frame)

    person_detections = []

    for detection in extract_detections(
        person_results
    ):
        normalized_name = detection.get(
            "normalized_name",
            ""
        )

        if normalized_name == "person":
            person_detections.append(
                detection
            )

    ppe_detections = extract_detections(
        ppe_results
    )

    person_detections.sort(
        key=lambda detection: (
            detection["box"][0],
            detection["box"][1]
        )
    )

    actual_worker_count = len(
        person_detections
    )

    unsafe_count = 0
    safe_count = 0

    for worker_number, person in enumerate(
        person_detections,
        start=1
    ):
        person_box = clamp_box(
            person["box"],
            image_width,
            image_height
        )

        x1, y1, x2, y2 = person_box

        status = get_worker_ppe_status(
            person_box,
            ppe_detections
        )

        unsafe = worker_is_unsafe(
            status
        )

        if unsafe:
            box_color = (0, 0, 220)
            safety_text = "UNSAFE"
            unsafe_count += 1
        else:
            box_color = (0, 190, 0)
            safety_text = "SAFE"
            safe_count += 1

        # Thin worker bounding box.
        cv2.rectangle(
            output_frame,
            (x1, y1),
            (x2, y2),
            box_color,
            box_thickness
        )

        worker_label = (
            f"Worker {worker_number} - "
            f"{safety_text}"
        )

        # Only one small label is placed above the worker.
        draw_compact_label(
            frame=output_frame,
            text=worker_label,
            x=x1,
            y=y1,
            background_color=box_color,
            font_scale=font_scale,
            text_thickness=text_thickness
        )

        # Small PPE status label is placed inside the
        # lower part of the box to avoid overlapping.
        ppe_label = (
            f"H:{status_word(status['helmet'])}  "
            f"V:{status_word(status['vest'])}  "
            f"G:{status_word(status['gloves'])}"
        )

        ppe_label_y = max(
            y1 + 32,
            y2 - 6
        )

        draw_compact_label(
            frame=output_frame,
            text=ppe_label,
            x=x1,
            y=ppe_label_y,
            background_color=(35, 35, 35),
            font_scale=small_font_scale,
            text_thickness=1
        )

        if status["fall"]:
            draw_fall_alert(
                output_frame,
                x1,
                y2,
                font_scale
            )

    if show_status_bar:
        draw_status_bar(
            frame=output_frame,
            worker_count=actual_worker_count,
            safe_count=safe_count,
            unsafe_count=unsafe_count,
            fps=fps
        )

    return output_frame