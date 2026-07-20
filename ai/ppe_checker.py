def analyze_ppe(ppe_results):
    summary = {
        "person": 0,
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

    for result in ppe_results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])
            class_name = result.names[class_id]

            if class_name == "Hardhat":
                summary["hardhat"] += 1

            elif class_name == "NO-Hardhat":
                summary["no_hardhat"] += 1

            elif class_name == "Safety Vest":
                summary["safety_vest"] += 1

            elif class_name == "NO-Safety Vest":
                summary["no_safety_vest"] += 1

            elif class_name == "Gloves":
                summary["gloves"] += 1

            elif class_name == "NO-Gloves":
                summary["no_gloves"] += 1

            elif class_name == "Goggles":
                summary["goggles"] += 1

            elif class_name == "NO-Goggles":
                summary["no_goggles"] += 1

            elif class_name == "Mask":
                summary["mask"] += 1

            elif class_name == "NO-Mask":
                summary["no_mask"] += 1

            elif class_name == "Fall-Detected":
                summary["fall_detected"] += 1

    return summary


def count_workers(person_results):

    count = 0

    for result in person_results:

        if result.boxes is None:
            continue

        for box in result.boxes:

            class_id = int(box.cls[0])

            if result.names[class_id] == "person":
                count += 1

    return count