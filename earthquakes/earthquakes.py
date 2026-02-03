"""
earthquakes.py

Utilities to fetch earthquake events from the INGV service, store them into an
SQLite database, and query the stored records.

The bounding box is read from a CSV file (default: bounding_box.csv) with the
following header:

minlatitude,maxlatitude,minlongitude,maxlongitude
"""

import csv
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

import requests


DB_DEFAULT_PATH = "earthquakes.db"
BOUNDING_BOX_CSV = "bounding_box.csv"
INGV_URL = "https://webservices.ingv.it/fdsnws/event/1/query"

EarthquakeRow = Tuple[str, str, float, float, float, str]


def read_bounding_box(csv_path: str = BOUNDING_BOX_CSV) -> Dict[str, float]:
    """
    Read a bounding box from a CSV file.

    The CSV file must contain exactly two rows:
    1) header: minlatitude,maxlatitude,minlongitude,maxlongitude
    2) values: numeric values for the bounding box

    Parameters
    ----------
    csv_path : str
        Path to the CSV file.

    Returns
    -------
    dict
        Dictionary with keys:
        minlatitude, maxlatitude, minlongitude, maxlongitude.

    Raises
    ------
    FileNotFoundError
        If the CSV file does not exist.
    ValueError
        If the CSV is malformed or values cannot be parsed as floats.
    """
    required_keys = {
        "minlatitude",
        "maxlatitude",
        "minlongitude",
        "maxlongitude",
    }

    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        try:
            keys = next(reader)
            values = next(reader)
        except StopIteration as exc:
            raise ValueError("bounding_box.csv must have a header and one row.") from exc

    if set(keys) != required_keys:
        raise ValueError(
            "bounding_box.csv header must be exactly: "
            "minlatitude,maxlatitude,minlongitude,maxlongitude"
        )

    try:
        bounding_box = {k: float(v) for k, v in zip(keys, values)}
    except ValueError as exc:
        raise ValueError("Bounding box values must be numeric floats.") from exc

    return bounding_box


def gather_earthquakes(days: int, bounding_box: Dict[str, float]) -> List[EarthquakeRow]:
    """
    Fetch earthquakes from INGV within the given bounding box for the last N days.

    Parameters
    ----------
    days : int
        How many days back from now (UTC) to query.
    bounding_box : dict
        Bounding box coordinates with keys:
        minlatitude, maxlatitude, minlongitude, maxlongitude.

    Returns
    -------
    list
        List of tuples:
        (day, time, magnitude, latitude, longitude, place)

    Raises
    ------
    requests.RequestException
        If the HTTP request fails.
    ValueError
        If the response JSON is not in the expected format.
    """
    endtime = datetime.now(timezone.utc)
    starttime = endtime - timedelta(days=days)

    params = {
        "format": "geojson",
        "starttime": starttime.strftime("%Y-%m-%dT%H:%M:%S"),
        "endtime": endtime.strftime("%Y-%m-%dT%H:%M:%S"),
        "minlatitude": bounding_box["minlatitude"],
        "maxlatitude": bounding_box["maxlatitude"],
        "minlongitude": bounding_box["minlongitude"],
        "maxlongitude": bounding_box["maxlongitude"],
    }

    response = requests.get(INGV_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    features = data.get("features")
    if not isinstance(features, list):
        raise ValueError("Unexpected INGV response: 'features' is missing or invalid.")

    earthquakes: List[EarthquakeRow] = []
    for event in features:
        props = event.get("properties", {})
        geom = event.get("geometry", {})
        coords = geom.get("coordinates", [])

        # Defensive parsing: skip incomplete records
        time_raw = props.get("time")
        mag_raw = props.get("mag")
        if time_raw is None or mag_raw is None or len(coords) < 2:
            continue

        try:
            t = datetime.strptime(time_raw, "%Y-%m-%dT%H:%M:%S.%f")
            magnitude = float(mag_raw)
            longitude = float(coords[0])
            latitude = float(coords[1])
        except (ValueError, TypeError):
            continue

        day = t.strftime("%Y-%m-%d")
        time_str = t.strftime("%H:%M:%S")
        place = props.get("place", "")

        earthquakes.append((day, time_str, magnitude, latitude, longitude, place))

    return earthquakes


def create_earthquake_db(
    earthquakes: List[EarthquakeRow],
    db_path: str = DB_DEFAULT_PATH,
) -> None:
    """
    Create (if missing) and populate the earthquakes SQLite database.

    Parameters
    ----------
    earthquakes : list
        List of earthquake rows:
        (day, time, magnitude, latitude, longitude, place)
    db_path : str
        SQLite database path.

    Returns
    -------
    None
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS earthquakes_db(
            day TEXT,
            time TEXT,
            mag REAL,
            latitude REAL,
            longitude REAL,
            place TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_earthquakes
        ON earthquakes_db(day, time, mag, latitude, longitude, place);
        """
    )

    cursor.executemany(
        """
        INSERT OR IGNORE INTO earthquakes_db(day, time, mag, latitude, longitude, place)
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        earthquakes,
    )

    conn.commit()
    cursor.close()
    conn.close()


def query_db(
    k: int,
    days: int,
    min_magnitude: float,
    db_path: str = DB_DEFAULT_PATH,
) -> List[EarthquakeRow]:
    """
    Query stored earthquakes from the database.

    Parameters
    ----------
    k : int
        Maximum number of results to return.
    days : int
        Only return earthquakes in the last N days.
    min_magnitude : float
        Only return earthquakes with magnitude >= min_magnitude.
    db_path : str
        SQLite database path.

    Returns
    -------
    list
        List of earthquake rows sorted by magnitude descending.
    """
    date_limit = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT day, time, mag, latitude, longitude, place
        FROM earthquakes_db
        WHERE mag >= ?
          AND day >= ?
        ORDER BY mag DESC
        LIMIT ?;
        """,
        (min_magnitude, date_limit, k),
    )

    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results


def print_earthquakes(earthquakes: List[EarthquakeRow]) -> None:
    """
    Print earthquake records in a readable format.

    Parameters
    ----------
    earthquakes : list
        Earthquake rows.

    Returns
    -------
    None
    """
    for day, time_str, mag, lat, lon, place in earthquakes:
        print(
            f"day: {day}, time: {time_str}, magnitude: {mag}\n"
            f"lat: {lat}, lon: {lon}, place: {place}\n"
        )