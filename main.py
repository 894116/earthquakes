"""
main.py

Command-line interface to fetch earthquakes, store them into SQLite,
and query the database.
"""

import argparse

from earthquakes.earthquakes import (
    create_earthquake_db,
    gather_earthquakes,
    print_earthquakes,
    query_db,
    read_bounding_box,
)


def main() -> None:
    """
    Run the CLI workflow.

    Steps:
    1) Read bounding box from CSV
    2) Fetch earthquakes from INGV
    3) Store results into SQLite
    4) Query and print the top earthquakes
    """
    parser = argparse.ArgumentParser(
        description=(
            "Fetch earthquakes, store them in SQLite, then query the database."
        )
    )
    parser.add_argument("--K", type=int, required=True, help="Number of results.")
    parser.add_argument("--days", type=int, required=True, help="Look back N days.")
    parser.add_argument(
        "--min-magnitude",
        type=float,
        required=True,
        help="Minimum magnitude threshold.",
    )

    args = parser.parse_args()

    bounding_box = read_bounding_box()
    earthquakes = gather_earthquakes(args.days, bounding_box)
    create_earthquake_db(earthquakes)

    results = query_db(args.K, args.days, args.min_magnitude)
    print_earthquakes(results)


if __name__ == "__main__":
    main()