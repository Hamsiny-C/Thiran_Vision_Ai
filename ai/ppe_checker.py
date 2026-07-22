def normalize_class_name(class_name):
    return (
        str(class_name)
        .strip()
        .lower()
        .replace("_", "-")
        .replace(" ", "-")
    )


def extract_detections(results):
    detections = []

    if results is None:
        return detections

    for result in results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])
            class_name = result.names[class_id]
            confidence = float(box.conf[0])

            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist()
            )

            detections.append({
                "class_id": class_id,
                "class_name": class_name,
                "normalized_name":
                    normalize_class_name(class_name),
                "confidence": confidence,
                "box": (x1, y1, x2, y2)
            })

    return detections


def count_workers(person_results):
    count = 0

    for detection in extract_detections(
        person_results
    ):
        if detection["normalized_name"] == "person":
            count += 1

    return count


def analyze_ppe(ppe_results):
    summary = {
        "hardhat": 0,
        "no_hardhat": 0,
        "safety_vest": 0,
        "no_safety_vest": 0,
        "gloves": 0,
        "no_gloves": 0,
        "goggles": 0,
        "no_goggles": 0,
        "mask": 0,
        "no_mask": 0,
        "fall_detected": 0
    }

    name_mapping = {
        "hardhat": "hardhat",
        "helmet": "hardhat",

        "no-hardhat": "no_hardhat",
        "no-helmet": "no_hardhat",

        "safety-vest": "safety_vest",
        "vest": "safety_vest",

        "no-safety-vest": "no_safety_vest",
        "no-vest": "no_safety_vest",

        "gloves": "gloves",
        "glove": "gloves",

        "no-gloves": "no_gloves",
        "no-glove": "no_gloves",

        "goggles": "goggles",
        "goggle": "goggles",

        "no-goggles": "no_goggles",
        "no-goggle": "no_goggles",

        "mask": "mask",

        "no-mask": "no_mask",

        "fall-detected": "fall_detected",
        "fall": "fall_detected"
    }

    for detection in extract_detections(
        ppe_results
    ):
        normalized_name = detection[
            "normalized_name"
        ]

        summary_key = name_mapping.get(
            normalized_name
        )

        if summary_key is not None:
            summary[summary_key] += 1

    return summary