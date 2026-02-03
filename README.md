# Earthquakes Project

This project is a Python-based application for fetching, processing and storing earthquake data.
It integrates data from two different seismic data sources: 
- **USGS** (https://earthquake.usgs.gov/fdsnws/event/1/) for global earthquakes; used by the function `get_earthquake(days_past)`, which retrieves the strongest earthquake worldwide over a given number of past days. This function is part of the original code provided with the repository and is kept for completeness.
- **INGV** (https://webservices.ingv.it/fdsnws/event/1/query?) for Italian earthquakes; used for the main part of the project developed in this assignment.  Earthquakes occurring within an Italian geographic bounding box are collected, stored in an SQLite database, and queried to retrieve the strongest events.

The main program (`main.py`) focuses on the INGV-based workflow.

## Repository Structure
**earthquakes/earthquakes.py** - Core module containing the main functions for fetching earthquake data, reading the bounding box, creating the SQLite database, querying it, and printing results.

**main.py** - Command-line interface that runs the main workflow: fetching earthquakes, storing them in the database, and printing the top K events.

**write_bouding_box.py + bounding_box.csv** - Utility script and corresponding CSV file defining the geographiv bounding box used to filter INGV earthquakes queries (currently Italy).




This repository contains a file named ```earthquakes.py``` that implements the ```get_earthquake(past_days)``` function. It queries the [USGS](https://earthquake.usgs.gov/fdsnws/event/1/) website to fetch the list of earthquakes registered in the last ```past_days``` days around the world and returns the one with the highest magnitude.
If you run the program, executing the main file with: ```python main.py``` it will  give you results similar to the following: 

```
$ python main.py
The largest earthquake of last 5 days had magnitude 7.7 and was located at 124km NNW of Lucea, Jamaica
```

Note that the project requires the ```json``` and ```requests``` module to run. Note also that USGS limits the maximum number of events returned to 20000, so that it may be useless to query  for events that have an age of more than a few days, as only the lastest 20000 events will be returned.

Edited by Neeti

Resolved the test issue. 

closes #10
