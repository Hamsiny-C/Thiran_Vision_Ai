import cv2
import numpy as np

from ai.ppe_checker import extract_detections


# ==========================================================
# PPE CLASS NAMES
# ==========================================================

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


# ==========================================================
# BOX FUNCTIONS
# ==========================================================

def clamp_box(box, image_width, image_height):
    x1, y1, x2, y2 = box

    x1 = max(0, min(int(x1), image_width - 1))
    y1 = max(0, min(int(y1), image_height - 1))
    x2 = max(0, min(int(x2), image_width - 1))
    y2 = max(0, min(int(y2), image_height - 1))

    return x1, y1, x2, y2


def box_center(box):
    x1, y1, x2, y2 = box

    return (
        int((x1 + x2) / 2),
        int((y1 + y2) / 2)
    )


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

    item_area = max(
        1,
        (ix2 - ix1) * (iy2 - iy1)
    )

    return intersection_area / item_area


def belongs_to_worker(person_box, ppe_box):
    center = box_center(ppe_box)

    if point_inside_box(center, person_box):
        return True

    overlap = intersection_over_item_area(
        person_box,
        ppe_box
    )

    return overlap >= 0.50


# ==========================================================
# PPE STATUS FUNCTIONS
# ==========================================================

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


def worker_is_unsafe(status):
    return (
        status["helmet"] is False
        or status["vest"] is False
        or status["gloves"] is False
        or status["fall"] is True
    )


def status_word(value):
    if value is True:
        return "YES"

    if value is False:
        return "NO"

    return "N/A"


# ==========================================================
# DRAW SMALL WORKER LABEL
# ==========================================================

def draw_worker_label(
    image,
    text,
    x,
    y,
    color
):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.42
    thickness = 1
    padding = 5

    (text_width, text_height), baseline = cv2.getTextSize(
        text,
        font,
        font_scale,
        thickness
    )

    label_width = text_width + padding * 2
    label_height = text_height + padding * 2 + baseline

    image_height, image_width = image.shape[:2]

    x = max(
        0,
        min(
            int(x),
            image_width - label_width - 1
        )
    )

    # Prefer drawing above the box.
    top = y - label_height

    # When there is no space above, draw inside the box.
    if top < 0:
        top = y

    bottom = min(
        image_height - 1,
        top + label_height
    )

    overlay = image.copy()

    cv2.rectangle(
        overlay,
        (x, top),
        (x + label_width, bottom),
        color,
        -1
    )

    cv2.addWeighted(
        overlay,
        0.78,
        image,
        0.22,
        0,
        image
    )

    cv2.putText(
        image,
        text,
        (
            x + padding,
            top + padding + text_height
        ),
        font,
        font_scale,
        (255, 255, 255),
        thickness,
        cv2.LINE_AA
    )


# ==========================================================
# RIGHT PANEL FUNCTIONS
# ==========================================================

def draw_panel_text(
    panel,
    text,
    x,
    y,
    font_scale=0.42,
    color=(230, 230, 230),
    thickness=1
):
    cv2.putText(
        panel,
        text,
        (int(x), int(y)),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA
    )


def draw_summary_box(
    panel,
    x,
    y,
    width,
    title,
    value,
    color
):
    box_height = 66

    cv2.rectangle(
        panel,
        (x, y),
        (x + width, y + box_height),
        (38, 42, 49),
        -1
    )

    cv2.rectangle(
        panel,
        (x, y),
        (x + 5, y + box_height),
        color,
        -1
    )

    draw_panel_text(
        panel,
        title,
        x + 14,
        y + 22,
        font_scale=0.34,
        color=(165, 172, 182)
    )

    draw_panel_text(
        panel,
        str(value),
        x + 14,
        y + 52,
        font_scale=0.72,
        color=(255, 255, 255),
        thickness=2
    )


def create_right_panel(
    image_height,
    worker_statuses,
    safe_count,
    unsafe_count
):
    panel_width = 340

    panel = np.full(
        (
            image_height,
            panel_width,
            3
        ),
        (22, 25, 30),
        dtype=np.uint8
    )

    # Header
    cv2.rectangle(
        panel,
        (0, 0),
        (panel_width, 76),
        (30, 34, 42),
        -1
    )

    draw_panel_text(
        panel,
        "THIRAN VISION AI",
        18,
        31,
        font_scale=0.58,
        color=(255, 255, 255),
        thickness=2
    )

    draw_panel_text(
        panel,
        "IMAGE SAFETY ANALYSIS",
        18,
        56,
        font_scale=0.34,
        color=(155, 165, 175)
    )

    worker_count = len(worker_statuses)

    card_y = 92
    card_width = 94

    draw_summary_box(
        panel,
        14,
        card_y,
        card_width,
        "WORKERS",
        worker_count,
        (255, 170, 0)
    )

    draw_summary_box(
        panel,
        123,
        card_y,
        card_width,
        "SAFE",
        safe_count,
        (0, 190, 0)
    )

    draw_summary_box(
        panel,
        232,
        card_y,
        card_width,
        "UNSAFE",
        unsafe_count,
        (0, 0, 220)
    )

    title_y = card_y + 96

    draw_panel_text(
        panel,
        "WORKER PPE STATUS",
        18,
        title_y,
        font_scale=0.43,
        color=(255, 255, 255),
        thickness=1
    )

    cv2.line(
        panel,
        (18, title_y + 12),
        (panel_width - 18, title_y + 12),
        (65, 70, 78),
        1
    )

    current_y = title_y + 30

    for worker in worker_statuses:
        card_height = 74

        if current_y + card_height > image_height - 16:
            draw_panel_text(
                panel,
                "Additional workers not shown",
                18,
                image_height - 18,
                font_scale=0.32,
                color=(160, 165, 170)
            )
            break

        status = worker["status"]
        unsafe = worker["unsafe"]

        if unsafe:
            safety_text = "UNSAFE"
            status_color = (0, 0, 220)
        else:
            safety_text = "SAFE"
            status_color = (0, 190, 0)

        cv2.rectangle(
            panel,
            (14, current_y),
            (
                panel_width - 14,
                current_y + card_height
            ),
            (36, 40, 47),
            -1
        )

        cv2.rectangle(
            panel,
            (14, current_y),
            (
                19,
                current_y + card_height
            ),
            status_color,
            -1
        )

        draw_panel_text(
            panel,
            f"Worker {worker['number']}",
            30,
            current_y + 24,
            font_scale=0.43,
            color=(255, 255, 255),
            thickness=1
        )

        draw_panel_text(
            panel,
            safety_text,
            245,
            current_y + 24,
            font_scale=0.35,
            color=status_color,
            thickness=1
        )

        ppe_text = (
            f"H:{status_word(status['helmet'])}  "
            f"V:{status_word(status['vest'])}  "
            f"G:{status_word(status['gloves'])}"
        )

        draw_panel_text(
            panel,
            ppe_text,
            30,
            current_y + 51,
            font_scale=0.36,
            color=(195, 200, 208)
        )

        if status["fall"]:
            draw_panel_text(
                panel,
                "FALL",
                275,
                current_y + 51,
                font_scale=0.34,
                color=(0, 0, 255),
                thickness=1
            )

        current_y += card_height + 10

    return panel


# ==========================================================
# MAIN IMAGE VISUALIZER
# ==========================================================

def draw_detection_dashboard(
    image,
    person_results,
    ppe_results,
    worker_count=None,
    ppe_summary=None,
    fps=None,
    show_status_bar=True
):
    if image is None:
        raise ValueError(
            "Input image cannot be None."
        )

    # The original image resolution is preserved.
    annotated_image = image.copy()

    image_height, image_width = annotated_image.shape[:2]

    person_detections = [
        detection
        for detection in extract_detections(
            person_results
        )
        if detection.get(
            "normalized_name",
            ""
        ) == "person"
    ]

    ppe_detections = extract_detections(
        ppe_results
    )

    person_detections.sort(
        key=lambda detection: (
            detection["box"][0],
            detection["box"][1]
        )
    )

    worker_statuses = []

    safe_count = 0
    unsafe_count = 0

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

        # Thin worker box.
        cv2.rectangle(
            annotated_image,
            (x1, y1),
            (x2, y2),
            box_color,
            2
        )

        # Only a small label is placed on the image.
        draw_worker_label(
            annotated_image,
            f"W{worker_number} {safety_text}",
            x1,
            y1,
            box_color
        )

        worker_statuses.append(
            {
                "number": worker_number,
                "status": status,
                "unsafe": unsafe
            }
        )

    right_panel = create_right_panel(
        image_height=image_height,
        worker_statuses=worker_statuses,
        safe_count=safe_count,
        unsafe_count=unsafe_count
    )

    # Add the panel without resizing the source image.
    final_output = cv2.hconcat(
        [
            annotated_image,
            right_panel
        ]
    )

    return final_output