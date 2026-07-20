"""
model.py
-------------------------

Prediction rules for the Industrial Safety System.

This file contains all threshold values used by the
Prediction Module.
"""

# -----------------------------
# Machine Health Thresholds
# -----------------------------

HIGH_TEMPERATURE = 80
HIGH_GAS = 150
HIGH_CURRENT = 22
HIGH_VIBRATION = 2.0
HIGH_NOISE = 85
HIGH_RPM = 1800


# -----------------------------
# Machine Health Score
# -----------------------------

MAX_HEALTH = 100


# -----------------------------
# Fire Risk Thresholds
# -----------------------------

FIRE_TEMPERATURE = 85
FIRE_GAS = 170


# -----------------------------
# Maintenance Thresholds
# -----------------------------

LOW_HEALTH = 40
MEDIUM_HEALTH = 70