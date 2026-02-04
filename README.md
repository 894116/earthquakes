# Earthquakes Project

This project is a Python-based application for fetching, processing and storing earthquake data.
It integrates data from **INGV** services (https://webservices.ingv.it/fdsnws/event/1/query?) for Italian earthquakes; used for the main part of the project developed in this assignment.  Earthquakes occurring within an Italian geographic bounding box are collected, stored in an SQLite database, and queried to retrieve the strongest events.

## Project Overview

The application performs the following steps:

1. Reads a geographic bounding box from a CSV file
2. Fetches earthquake data from INGV for the last *N* days
3. Stores the data in a local SQLite database
4. Queries the database to retrieve the strongest earthquakes
5. Prints the results in a readable format
6. Provides a minimal unittest suite to validate the main logic


## Main files
**earthquakes/earthquakes.py** - Core module containing the main functions for fetching earthquake data, reading the bounding box, creating the SQLite database, querying stored data, and printing results.

**main.py** - Command-line interface that runs the main workflow: fetching earthquakes, storing them in the database, and printing the top K events based on user-defined parameters.

**write_bouding_box.py + bounding_box.csv** - Utility script and corresponding CSV file defining the geographic bounding box used to filter INGV earthquakes queries (currently Italy).

**test_project.py** - Test suite implemented using Python’s `unittest` framework to validate the main functionalities of the project.

## How the program works
The core logic of the project is implemented in the file `earthquakes/earthquakes.py`.
This module handles the entire earthquake data pipeline: it reads the geographic bounding box from a CSV file, fetches earthquake events from the INGV web service within the selected time window, stores the data in an SQLite database, and allows querying the strongest earthquakes based on user-defined parameters.

The main entry point of the project is `main.py`, which provides a command-line interface to run the complete workflow.

If you run the program from the command line, you can specify:
- how many days in the past to look back,
- the minimum magnitude threshold,
- and the number of strongest earthquakes to display.

For example, running:
```
python main.py --days 7 --min_magnitude 3.0 --K 5
```

will fetch earthquakes from the last 7 days within the Italian bounding box, store them in the dataset, and print the top5 strongest events with magnitude grater than ore equal to 3.0.

The results are printed in readable format, including date, time, magnitude, location, and geographic coordinates.

## Requirements

The project relies on standard Python libraries such as `datetime`, `csv`, `sqlite3`, and `argparse`, and uses the external `requests` module to retrieve earthquake data from the INGV web service.
