"""
maintenance.py
------------------------

Predictive Maintenance Module
"""

from prediction.model import LOW_HEALTH, MEDIUM_HEALTH


def predict_maintenance(machine_health):
    """
    Predict maintenance details
    based on machine health.
    """

    if machine_health >= 90:

        return {
            "maintenance_required": False,
            "maintenance_days": 30,
            "bearing_wear": "Healthy",
            "priority": "Low"
        }

    elif machine_health >= MEDIUM_HEALTH:

        return {
            "maintenance_required": False,
            "maintenance_days": 15,
            "bearing_wear": "Slight Wear",
            "priority": "Medium"
        }

    elif machine_health >= LOW_HEALTH:

        return {
            "maintenance_required": True,
            "maintenance_days": 7,
            "bearing_wear": "Moderate Wear",
            "priority": "High"
        }

    else:

        return {
            "maintenance_required": True,
            "maintenance_days": 2,
            "bearing_wear": "Critical Wear",
            "priority": "Critical"
        }


if __name__ == "__main__":

    print(predict_maintenance(95))

    print(predict_maintenance(70))

    print(predict_maintenance(35))