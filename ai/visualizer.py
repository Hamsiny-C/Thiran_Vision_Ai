import cv2
from datetime import datetime


# -------------------- COLORS --------------------

SAFE_COLOR = (60, 220, 80)
DANGER_COLOR = (0, 0, 255)
WARNING_COLOR = (0, 165, 255)

CYAN = (255, 220, 0)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (170, 170, 170)

PANEL_COLOR = (18, 24, 32)


# -------------------- BASIC HELPERS --------------------

def box_center(box_coordinates):
    x1, y1, x2, y2 = box_coordinates

    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2

    return center_x, center_y


def point_inside_person(center_x, center_y, person_box):
    px1, py1, px2, py2 = person_box

    return (
        px1 <= center_x <= px2
        and py1 <= center_y <= py2
    )


def get_ppe_detections(ppe_results):
    detections = []

    for result in ppe_results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            detections.append({
                "class_name": class_name,
                "confidence": confidence,
                "box": (x1, y1, x2, y2)
            })

    return detections


# -------------------- PPE CHECKING --------------------

def check_worker_ppe(person_box, ppe_detections):
    helmet_status = "UNKNOWN"
    vest_status = "UNKNOWN"

    helmet_confidence = 0.0
    vest_confidence = 0.0

    for detection in ppe_detections:

        class_name = detection["class_name"]
        confidence = detection["confidence"]
        ppe_box = detection["box"]

        center_x, center_y = box_center(ppe_box)

        if not point_inside_person(
            center_x,
            center_y,
            person_box
        ):
            continue

        if class_name == "Hardhat":

            if confidence > helmet_confidence:
                helmet_status = "SAFE"
                helmet_confidence = confidence

        elif class_name == "NO-Hardhat":

            if confidence > helmet_confidence:
                helmet_status = "MISSING"
                helmet_confidence = confidence

        elif class_name == "Safety Vest":

            if confidence > vest_confidence:
                vest_status = "SAFE"
                vest_confidence = confidence

        elif class_name == "NO-Safety Vest":

            if confidence > vest_confidence:
                vest_status = "MISSING"
                vest_confidence = confidence

    return (
        helmet_status,
        vest_status,
        helmet_confidence,
        vest_confidence
    )


def get_overall_status(
    helmet_status,
    vest_status
):
    if (
        helmet_status == "MISSING"
        or vest_status == "MISSING"
    ):
        return "UNSAFE", DANGER_COLOR

    if (
        helmet_status == "SAFE"
        and vest_status == "SAFE"
    ):
        return "SAFE", SAFE_COLOR

    return "CHECK PPE", WARNING_COLOR


# -------------------- TEXT DRAWING --------------------

def draw_text_with_background(
    image,
    text,
    x,
    y,
    text_color,
    background_color,
    font_scale=0.45,
    thickness=1
):
    height, width = image.shape[:2]

    text_size, baseline = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        thickness
    )

    text_width, text_height = text_size

    x = max(0, min(x, width - text_width - 14))
    y = max(text_height + 10, min(y, height - baseline - 5))

    cv2.rectangle(
        image,
        (x, y - text_height - 9),
        (x + text_width + 12, y + baseline + 4),
        background_color,
        -1
    )

    cv2.putText(
        image,
        text,
        (x + 6, y - 3),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        text_color,
        thickness,
        cv2.LINE_AA
    )


# -------------------- WORKER DRAWING --------------------

def draw_worker(
    output,
    person_box,
    person_confidence,
    worker_number,
    helmet_status,
    vest_status
):
    x1, y1, x2, y2 = person_box

    overall_status, status_color = get_overall_status(
        helmet_status,
        vest_status
    )

    cv2.rectangle(
        output,
        (x1, y1),
        (x2, y2),
        status_color,
        2
    )

    worker_text = (
        f"WORKER {worker_number} "
        f"{person_confidence:.2f}"
    )

    worker_label_y = y1 - 7

    if worker_label_y < 25:
        worker_label_y = y1 + 25

    draw_text_with_background(
        output,
        worker_text,
        x1,
        worker_label_y,
        WHITE,
        BLACK,
        font_scale=0.43,
        thickness=1
    )

    status_y = y2 + 25

    if status_y >= output.shape[0]:
        status_y = y2 - 8

    draw_text_with_background(
        output,
        overall_status,
        x1,
        status_y,
        WHITE,
        status_color,
        font_scale=0.50,
        thickness=2
    )

    helmet_text = (
        "Helmet: YES"
        if helmet_status == "SAFE"
        else "Helmet: NO"
        if helmet_status == "MISSING"
        else "Helmet: ?"
    )

    vest_text = (
        "Vest: YES"
        if vest_status == "SAFE"
        else "Vest: NO"
        if vest_status == "MISSING"
        else "Vest: ?"
    )

    details_text = (
        f"{helmet_text} | {vest_text}"
    )

    details_y = status_y + 22

    if details_y >= output.shape[0]:
        details_y = y2 - 28

    cv2.putText(
        output,
        details_text,
        (x1, details_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        status_color,
        1,
        cv2.LINE_AA
    )

    return overall_status


# -------------------- DASHBOARD --------------------

def draw_dashboard(
    output,
    statistics,
    fps=None
):
    image_height, image_width = output.shape[:2]

    panel_x1 = 12
    panel_y1 = 12

    panel_width = min(
        390,
        image_width - 24
    )

    panel_height = min(
        245,
        image_height - 24
    )

    panel_x2 = panel_x1 + panel_width
    panel_y2 = panel_y1 + panel_height

    overlay = output.copy()

    cv2.rectangle(
        overlay,
        (panel_x1, panel_y1),
        (panel_x2, panel_y2),
        PANEL_COLOR,
        -1
    )

    blended = cv2.addWeighted(
        overlay,
        0.86,
        output,
        0.14,
        0
    )

    output[:] = blended

    cv2.rectangle(
        output,
        (panel_x1, panel_y1),
        (panel_x2, panel_y2),
        CYAN,
        2
    )

    cv2.putText(
        output,
        "THIRAN VISION AI",
        (panel_x1 + 15, panel_y1 + 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        CYAN,
        2,
        cv2.LINE_AA
    )

    cv2.putText(
        output,
        "INDUSTRIAL PPE MONITORING",
        (panel_x1 + 15, panel_y1 + 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        WHITE,
        1,
        cv2.LINE_AA
    )

    cv2.line(
        output,
        (panel_x1 + 15, panel_y1 + 61),
        (panel_x2 - 15, panel_y1 + 61),
        GRAY,
        1
    )

    left_x = panel_x1 + 15
    right_x = panel_x1 + 205

    row_1 = panel_y1 + 87
    row_2 = panel_y1 + 113
    row_3 = panel_y1 + 139
    row_4 = panel_y1 + 165
    row_5 = panel_y1 + 191

    cv2.putText(
        output,
        f"Workers       : {statistics['workers']}",
        (left_x, row_1),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.46,
        WHITE,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        output,
        f"Safe          : {statistics['safe']}",
        (left_x, row_2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.46,
        SAFE_COLOR,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        output,
        f"Unsafe        : {statistics['unsafe']}",
        (right_x, row_2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.46,
        DANGER_COLOR,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        output,
        f"Helmet YES    : {statistics['helmet_yes']}",
        (left_x, row_3),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        SAFE_COLOR,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        output,
        f"Helmet NO : {statistics['helmet_no']}",
        (right_x, row_3),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        DANGER_COLOR,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        output,
        f"Vest YES      : {statistics['vest_yes']}",
        (left_x, row_4),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        SAFE_COLOR,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        output,
        f"Vest NO   : {statistics['vest_no']}",
        (right_x, row_4),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        DANGER_COLOR,
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        output,
        f"Check PPE     : {statistics['check']}",
        (left_x, row_5),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.43,
        WARNING_COLOR,
        1,
        cv2.LINE_AA
    )

    current_time = datetime.now().strftime(
        "%H:%M:%S"
    )

    footer_y = panel_y2 - 18

    if fps is not None:

        cv2.putText(
            output,
            f"FPS: {fps:.1f}",
            (left_x, footer_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            WHITE,
            1,
            cv2.LINE_AA
        )

    cv2.putText(
        output,
        current_time,
        (panel_x2 - 85, footer_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        WHITE,
        1,
        cv2.LINE_AA
    )


# -------------------- MAIN VISUALIZER --------------------

def draw_detection_dashboard(
    image,
    person_results,
    ppe_results,
    worker_count,
    ppe_summary=None,
    fps=None
):
    output = image.copy()

    ppe_detections = get_ppe_detections(
        ppe_results
    )

    statistics = {
        "workers": 0,
        "safe": 0,
        "unsafe": 0,
        "check": 0,
        "helmet_yes": 0,
        "helmet_no": 0,
        "helmet_unknown": 0,
        "vest_yes": 0,
        "vest_no": 0,
        "vest_unknown": 0
    }

    worker_number = 1

    for result in person_results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])
            class_name = result.names[class_id]

            if class_name.lower() != "person":
                continue

            confidence = float(box.conf[0])

            person_box = tuple(
                map(int, box.xyxy[0])
            )

            (
                helmet_status,
                vest_status,
                helmet_confidence,
                vest_confidence
            ) = check_worker_ppe(
                person_box,
                ppe_detections
            )

            overall_status = draw_worker(
                output,
                person_box,
                confidence,
                worker_number,
                helmet_status,
                vest_status
            )

            statistics["workers"] += 1

            if overall_status == "SAFE":
                statistics["safe"] += 1

            elif overall_status == "UNSAFE":
                statistics["unsafe"] += 1

            else:
                statistics["check"] += 1

            if helmet_status == "SAFE":
                statistics["helmet_yes"] += 1

            elif helmet_status == "MISSING":
                statistics["helmet_no"] += 1

            else:
                statistics["helmet_unknown"] += 1

            if vest_status == "SAFE":
                statistics["vest_yes"] += 1

            elif vest_status == "MISSING":
                statistics["vest_no"] += 1

            else:
                statistics["vest_unknown"] += 1

            worker_number += 1

    # Use the real visualized worker count.
    statistics["workers"] = worker_number - 1

    draw_dashboard(
        output,
        statistics,
        fps
    )

    return output