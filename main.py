import argparse
from earthquakes.earthquakes import (
    gather_earthquakes,
    create_earthquake_db,
    query_db,
    print_earthquakes,
    get_bounding_box_names,
)

def main():
    box_choices = get_bounding_box_names()

    parser = argparse.ArgumentParser(
        description="Fetch earthquakes, store them in SQLite, then query the database."
    )

    parser.add_argument("--K", type=int, required=True)
    parser.add_argument("--days", type=int, required=True)
    parser.add_argument("--min-magnitude", type=float, required=True)
    parser.add_argument("--box", required=True, choices=box_choices)

    args = parser.parse_args()

    # 1) Fetch earthquakes for the selected region + days
    earthquakes = gather_earthquakes(args.days, box_name=args.box)

    # 2) Create DB + insert records (creates table earthquakes_db if missing)
    create_earthquake_db(earthquakes)

    # 3) Query DB + print results
    results = query_db(args.K, args.days, args.min_magnitude)
    print_earthquakes(results)

if __name__ == "__main__":
    main()