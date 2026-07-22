import os


# ==================================================
# MODEL PATHS
# ==================================================

PERSON_MODEL_PATH = os.path.join(
    "ai",
    "models",
    "yolo11n.pt"
)

PPE_MODEL_PATH = os.path.join(
    "ai",
    "models",
    "ppe",
    "best.pt"
)


# ==================================================
# IMAGE DETECTION SETTINGS
# ==================================================

# Lower confidence helps detect partially hidden workers.
IMAGE_PERSON_CONFIDENCE = 0.18

# PPE confidence kept slightly higher to reduce false detections.
IMAGE_PPE_CONFIDENCE = 0.20

# High resolution for better image accuracy.
IMAGE_SIZE = 1280


# ==================================================
# VIDEO DETECTION SETTINGS
# ==================================================

VIDEO_PERSON_CONFIDENCE = 0.20
VIDEO_PPE_CONFIDENCE = 0.22

# Reduced size for faster CPU video processing.
VIDEO_IMAGE_SIZE = 640

# AI detection runs once every 3 frames.
# All frames are still written to the output video.
VIDEO_PROCESS_EVERY_N_FRAMES = 3


# ==================================================
# LIVE CAMERA SETTINGS
# ==================================================

CAMERA_PERSON_CONFIDENCE = 0.25
CAMERA_PPE_CONFIDENCE = 0.25

# Smaller size gives smoother live detection on CPU.
CAMERA_IMAGE_SIZE = 416

CAMERA_ID = 0

# AI runs once every 3 camera frames.
PROCESS_EVERY_N_FRAMES = 3


# ==================================================
# NMS SETTINGS
# ==================================================

PERSON_IOU = 0.50
PPE_IOU = 0.45


# ==================================================
# OUTPUT SETTINGS
# ==================================================

OUTPUT_DIRECTORY = os.path.join(
    "ai",
    "output"
)

IMAGE_PATH = ""
VIDEO_PATH = ""