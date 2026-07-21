"""
Tracking Configuration
----------------------
Stores all configurable values used by the tracking module.
"""

# Maximum number of frames a worker can disappear
# before the tracker removes the worker.
MAX_MISSING_FRAMES = 30

# Maximum distance (pixels) allowed to match
# a worker with a previous detection.
MAX_TRACKING_DISTANCE = 100

# Seconds before a worker is considered
# stationary.
IDLE_TIME_THRESHOLD = 10

# Seconds before a worker is considered
# to be loitering.
LOITERING_TIME_THRESHOLD = 30

# Restricted zone polygon.
# Modify these coordinates according
# to your camera view.
RESTRICTED_ZONE = [
    (100, 100),
    (500, 100),
    (500, 400),
    (100, 400)
]

# Worker display color (Green)
WORKER_COLOR = (0, 255, 0)

# Restricted zone color (Red)
ZONE_COLOR = (0, 0, 255)

# Worker ID text color (White)
TEXT_COLOR = (255, 255, 255)

# Font scale for labels
FONT_SCALE = 0.6

# Bounding box thickness
BOX_THICKNESS = 2

# Line thickness
LINE_THICKNESS = 2

# Enable debug information
DEBUG = True