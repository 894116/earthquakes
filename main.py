import argparse
from earthquakes.earthquakes import query_db, print_earthquakes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("K", type = int)
    parser.add_argument("days", type = int)
    parser.add_argument("min_magnitude", type = float)
    args = parser.parse_args()

    earthquakes = query_db(args.K, args.days, args.min_magnitude)
    print_earthquakes(earthquakes)


if __name__ == "__main__":
    main()