"""
utils.py
------------------------

Utility Functions
"""


def print_heading(title):

    print()

    print("=" * 50)

    print(title)

    print("=" * 50)


def health_status(health):

    if health >= 90:
        return "Excellent"

    elif health >= 70:
        return "Good"

    elif health >= 40:
        return "Warning"

    else:
        return "Critical"