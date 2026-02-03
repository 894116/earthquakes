"""
earthquakes.py

Utilities to:
- read a bounding box from bounding_box.csv
- fetch earthquake events from INGV (GeoJSON)
- store them into an SQLite database
- query and print stored records
"""

from __future__ import annotations

import csv
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

import requests

BOUNDING_BOX_CSV = "bounding_box.csv"
DB_DEFAULT_PATH = "earthquakes.db"
INGV_URL = "https://webservices.ingv.it/fdsnws/event/1/query"

EarthquakeRow = Tuple[str, str, float, float, float, str]


def read_bounding_box(csv_path: str = BOUNDING_BOX_CSV) -> Dict[str, float]:
    """
    Read bounding box from a 2-line CSV:
    header: minlatitude,maxlatitude,minlongitude,maxlongitude
    values: 35.0,47.5,5.0,20.0

    Parameters
    ----------
    csv_path : str
        Path to the CSV file.

    Returns
    -------
    dict[str, float]
        Bounding box dict with required keys.

    Raises
    ------
    ValueError
        If the file is empty, missing columns, or contains non-numeric values.
    FileNotFoundError
        If the CSV file does not exist.
    """
    required = {"minlatitude", "maxlatitude", "minlongitude", "maxlongitude"}

    with open(csv_path, newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        try:
            keys = next(reader)
            values = next(reader)
        except StopIteration as exc:
            raise ValueError("bounding_box.csv must contain header + one values row") from exc

    if not required.issubset(set(keys)):
        raise ValueError(
            "bounding_box.csv must contain columns: "
            "minlatitude,maxlatitude,minlongitude,maxlongitude"
        )

    raw = dict(zip(keys, values))
    try:
        return {k: float(raw[k]) for k in required}
    except (KeyError, ValueError) as exc:
        raise ValueError("bounding_box.csv values must be numeric") from exc


def gather_earthquakes(days: int) -> List[EarthquakeRow]:
    """
    Fetch earthquakes from INGV for the last `days` days within the bounding box.

    Parameters
    ----------
    days : int
        Days back from now (UTC).

    Returns
    -------
    list[EarthquakeRow]
        Rows: (day, time, mag, latitude, longitude, place)
    """
    bounding_box = read_bounding_box()

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
    events = response.json()

    earthquakes: List[EarthquakeRow] = []

    for event in events.get("features", []):
        props = event.get("properties", {})
        geom = event.get("geometry", {})
        coords = geom.get("coordinates", [None, None, None])

        time_str = props.get("time")
        mag = props.get("mag")

        if time_str is None or mag is None or coords[0] is None or coords[1] is None:
            continue

        # INGV time can be "...%f" or without microseconds
        try:
            t = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            t = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")

        day = t.strftime("%Y-%m-%d")
        tm = t.strftime("%H:%M:%S")

        earthquakes.append(
            (
                day,
                tm,
                float(mag),
                float(coords[1]),
                float(coords[0]),
                str(props.get("place", "")),
            )
        )

    return earthquakes


def create_earthquake_db(days: int, db_path: str = DB_DEFAULT_PATH) -> None:
    """
    Fetch earthquakes for `days` days and store them in SQLite.

    Parameters
    ----------
    days : int
        Days of data to fetch.
    db_path : str
        SQLite database path.
    """
    earthquakes = gather_earthquakes(days)

    with sqlite3.connect(db_path) as conn:
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


def query_db(
    k: int,
    days: int,
    min_magnitude: float,
    db_path: str = DB_DEFAULT_PATH,
) -> List[EarthquakeRow]:
    """
    Query the K strongest earthquakes in the last `days` days
    with magnitude >= min_magnitude.

    Returns
    -------
    list[EarthquakeRow]
        Rows ordered by magnitude decreasing.
    """
    date_limit = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    with sqlite3.connect(db_path) as conn:
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
        return cursor.fetchall()


def print_earthquakes(earthquakes: List[EarthquakeRow]) -> None:
    """
    Print earthquake rows in a readable format.
    """
    for day, tm, mag, lat, lon, place in earthquakes:
        print(
            f"day: {day}, time: {tm}, magnitude: {mag}\n"
            f"lat: {lat}, lon: {lon}, place: {place}\n"
        )