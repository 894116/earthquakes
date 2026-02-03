"""
write_bounding_box.py

Create (or overwrite) bounding_box.csv with a default Italy bounding box.
"""

import csv

BOUNDING_BOX_CSV = "bounding_box.csv"


def main() -> None:
    """Write a 2-line CSV containing bounding box coordinates for Italy."""
    bounding_box = {
        "minlatitude": 35.0,
        "maxlatitude": 47.5,
        "minlongitude": 5.0,
        "maxlongitude": 20.0,
    }

    with open(BOUNDING_BOX_CSV, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(bounding_box.keys())
        writer.writerow(bounding_box.values())


if __name__ == "__main__":
    main()