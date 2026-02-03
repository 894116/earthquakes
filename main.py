"""
main.py

Command-line interface to:
1) fetch earthquakes (last N days) and store them into SQLite
2) query the database and print results
"""

import argparse

from earthquakes.earthquakes import create_earthquake_db, print_earthquakes, query_db


def main() -> None:
    """Parse CLI args, build DB, query DB, print results."""
    parser = argparse.ArgumentParser(
        description="Fetch earthquakes, store them in SQLite, then query results."
    )
    parser.add_argument("--K", type=int, required=True, help="Number of results to show.")
    parser.add_argument("--days", type=int, required=True, help="Look back window in days.")
    parser.add_argument(
        "--min-magnitude",
        type=float,
        required=True,
        help="Minimum magnitude threshold.",
    )

    args = parser.parse_args()

    # Step 1: build/refresh database for the chosen time window
    create_earthquake_db(args.days)

    # Step 2: query and print
    results = query_db(args.K, args.days, args.min_magnitude)
    print_earthquakes(results)


if __name__ == "__main__":
    main()