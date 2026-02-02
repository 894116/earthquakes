import requests
import datetime
import json

BOUNDING_BOX_CSV = "bounding_box.csv"

def get_bounding_box_names():
    #only one bounding box is defined in this lab
    return ["italy"]

USGS_URL = 'https://earthquake.usgs.gov/fdsnws/event/1/query?starttime={}&format=geojson&limit=20000'

def get_earthquake(days_past):
    #get the date of today - days_past days at 00 AM
    start_date = (datetime.datetime.now() + datetime.timedelta(days=-days_past)).strftime("%Y-%m-%d")
    url = USGS_URL.format(start_date)
    r = requests.get(url)
    events = json.loads(requests.get(url).text)
    magnitude = 0
    place = ''
    for event in events['features']:
        try:
            mag = float(event['properties']['mag'])
        except TypeError:
            pass
        if mag > magnitude:
            magnitude = mag
            place = event['properties']['place']
    return magnitude, place

import csv
import requests
from datetime import datetime, timedelta

def read_bounding_box():
    with open('bounding_box.csv', newline = '') as file:
        reader = csv.reader(file)
        keys = next(reader)
        values = next(reader)
    return {k:float(v) for k,v in zip(keys, values)}

def read_bounding_box_from_boxes(box_name):
    # since you currently only have one box, ignore box_name
    return read_bounding_box()

def gather_earthquakes(days, box_name="italy"):
    bounding_box = read_bounding_box_from_boxes(box_name)
    url = "https://webservices.ingv.it/fdsnws/event/1/query?"

    bounding_box = read_bounding_box()
    from datetime import timezone
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

    response = requests.get(url, params=params)
    events = response.json()

    earthquakes = []
    for event in events['features']:
        props = event['properties']
        geom = event['geometry']

        t = datetime.strptime(props['time'], "%Y-%m-%dT%H:%M:%S.%f")
        day = t.strftime("%Y-%m-%d")
        time = t.strftime("%H:%M:%S")

        magnitude = props['mag']
        place = props.get('place',"")

        longitude = geom['coordinates'][0]
        latitude = geom['coordinates'][1]
        earthquakes.append(
            (day, time, magnitude, latitude, longitude, place)
        )
    return earthquakes

import sqlite3
def create_earthquake_db(earthquakes, db_path='earthquakes.db'):
    """
    Create an SQL Database and stores earthquakes record.
    'earthquakes' must be a list of tuples (day, time, magnitude, latitude, longitude, place)
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()


    create_sql = """
    CREATE TABLE IF NOT EXISTS earthquakes_db(
        day TEXT,
        time TEXT, 
        mag REAL, 
        latitude REAL, 
        longitude REAL, 
        place TEXT
    ); 
    """
    cursor.execute(create_sql)

    cursor.execute("""
    CREATE UNIQUE INDEX IF NOT EXISTS uq_earthquakes
    ON earthquakes_db (day, time, mag, latitude, longitude, place);
    """)

    conn.commit()

    insert_sql = (
        "INSERT OR IGNORE INTO earthquakes_db (day, time, mag, latitude, longitude, place) "
        "VALUES (?, ?, ?, ?, ?, ?)"
    )


    cursor.executemany(insert_sql, earthquakes)

    cursor.execute("""
    DELETE FROM earthquakes_db
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM earthquakes_db
        GROUP BY day, time, mag, latitude, longitude, place
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()


def query_db(K, days, min_magnitude, db_path='earthquakes.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    date_limit = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    cursor.execute(
        """
        SELECT day, time, mag, latitude, longitude, place
        FROM earthquakes_db
        WHERE mag >= ?
            AND day >= ?
        ORDER BY mag DESC
        LIMIT ?
        """,
        (min_magnitude, date_limit, K)
    )

    results = cursor.fetchall()
    conn.close()
    return results

def print_earthquakes(earthquakes):
    for eq in earthquakes:
        day, time, mag, latitude, longitude, place = eq

        print(
            f"day: {day}, time: {time}, magnitude: {mag},\n"
            f"lat: {latitude}, lon: {longitude}, place: {place}"
        )

def get_bounding_box_names(csv_path="bounding_box.csv"):
    names = []
    with open(csv_path, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            names.append(row["name"])
    return names


import csv

BOUNDING_BOX_CSV = "bounding_box.csv"


def get_bounding_box_names():
    with open(BOUNDING_BOX_CSV, newline="") as file:
        reader = csv.DictReader(file)
        return [row["name"] for row in reader]


def read_bounding_box(box_name):
    with open(BOUNDING_BOX_CSV, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["name"] == box_name:
                return {
                    "minlatitude": float(row["minlatitude"]),
                    "maxlatitude": float(row["maxlatitude"]),
                    "minlongitude": float(row["minlongitude"]),
                    "maxlongitude": float(row["maxlongitude"]),
                }

    raise ValueError(f"Bounding box '{box_name}' not found")