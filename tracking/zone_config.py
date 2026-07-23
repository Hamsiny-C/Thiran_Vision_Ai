from typing import Dict, List, Tuple


Point = Tuple[int, int]
Polygon = List[Point]


# ==========================================================
# RESTRICTED ZONE SETTINGS
# ==========================================================

ENABLE_RESTRICTED_ZONE = True

# Show zone boundary on output video
SHOW_ZONE = True

# Show zone name on output video
SHOW_ZONE_NAME = True

# Show alert text when worker enters zone
SHOW_ZONE_ALERT = True

# Draw worker movement path
SHOW_TRAJECTORY = True

# Number of recent movement points to display
MAX_TRAJECTORY_POINTS = 30


# ==========================================================
# ZONE COLORS - BGR FORMAT
# ==========================================================

ZONE_BORDER_COLOR = (0, 0, 255)
ZONE_FILL_COLOR = (0, 0, 180)
ZONE_TEXT_COLOR = (255, 255, 255)

SAFE_WORKER_COLOR = (0, 255, 0)
DANGER_WORKER_COLOR = (0, 0, 255)

TRAJECTORY_COLOR = (255, 200, 0)


# ==========================================================
# ZONE DISPLAY SETTINGS
# ==========================================================

ZONE_BORDER_THICKNESS = 3
ZONE_FILL_OPACITY = 0.25

WORKER_BOX_THICKNESS = 2
TRAJECTORY_THICKNESS = 2

ALERT_DURATION_SECONDS = 3.0


# ==========================================================
# RESTRICTED ZONES
# ==========================================================
#
# Coordinates are written for the original video frame.
#
# Format:
#
# "zone_name": {
#     "name": "Display Name",
#     "points": [
#         (x1, y1),
#         (x2, y2),
#         (x3, y3),
#         (x4, y4)
#     ],
#     "enabled": True
# }
#
# You can change these coordinates according to your video.
# ==========================================================

RESTRICTED_ZONES: Dict[str, Dict] = {
    "danger_zone": {
        "name": "DANGER ZONE",
        "points": [
            (520, 180),
            (900, 180),
            (980, 620),
            (460, 620)
        ],
        "enabled": True
    }
}


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_enabled_zones() -> Dict[str, Dict]:
    """
    Return only enabled restricted zones.
    """

    if not ENABLE_RESTRICTED_ZONE:
        return {}

    return {
        zone_id: zone_data
        for zone_id, zone_data in RESTRICTED_ZONES.items()
        if zone_data.get("enabled", False)
    }


def get_zone_points(zone_id: str) -> Polygon:
    """
    Return polygon points of a restricted zone.
    """

    zone = RESTRICTED_ZONES.get(zone_id)

    if zone is None:
        return []

    return zone.get("points", [])


def get_zone_name(zone_id: str) -> str:
    """
    Return display name of a restricted zone.
    """

    zone = RESTRICTED_ZONES.get(zone_id)

    if zone is None:
        return zone_id

    return zone.get("name", zone_id)


def update_zone_points(
    zone_id: str,
    points: Polygon
) -> bool:
    """
    Update zone coordinates during runtime.
    """

    if zone_id not in RESTRICTED_ZONES:
        return False

    if len(points) < 3:
        return False

    RESTRICTED_ZONES[zone_id]["points"] = points

    return True


def add_zone(
    zone_id: str,
    name: str,
    points: Polygon,
    enabled: bool = True
) -> bool:
    """
    Add a new restricted zone.
    """

    if not zone_id:
        return False

    if len(points) < 3:
        return False

    RESTRICTED_ZONES[zone_id] = {
        "name": name,
        "points": points,
        "enabled": enabled
    }

    return True


def remove_zone(zone_id: str) -> bool:
    """
    Remove a restricted zone.
    """

    if zone_id not in RESTRICTED_ZONES:
        return False

    del RESTRICTED_ZONES[zone_id]

    return True