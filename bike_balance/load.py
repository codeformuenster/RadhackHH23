"""Load poetry file."""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytz
import requests


def load_station_datastreams() -> pd.DataFrame:
    DATASTREAMS_URL = (
        "https://iot.hamburg.de/v1.1/Datastreams?"
        "$count=true&"
        "$filter=properties/serviceName%20eq%20%27HH_STA_StadtRad%27%20"
        "and%20properties/layerName%20eq%20%27Fahrraeder%27"
    )

    datastream_result = []
    response = requests.get(DATASTREAMS_URL)

    print("scrape datastreams...")
    while True:
        print(response.json().get("@iot.nextLink"))
        # Extract the data from the response
        data = response.json()["value"]
        # Append the data to the results list
        datastream_result += data
        # Get the URL of the next page of results
        next_url = response.json()["@iot.nextLink"]
        # Send the next request to the API
        response = requests.get(next_url)
        # If there is no next page, break the loop
        if not response.json().get("@iot.nextLink"):
            break
    print("datastreams scraped.")

    # save datastream data to file
    DATASTREAM_JSON = Path("data/datastreams.json")
    json_string = json.dumps(datastream_result, indent=2)
    with open(DATASTREAM_JSON, "w") as f:
        f.write(json_string)

    # parse datastream data
    station_datastream_links = [
        {
            "station_uuid": record["name"].strip("Fahrräder an StadtRad-Station "),
            "datastrem_link": record["Observations@iot.navigationLink"],
        }
        for record in datastream_result
    ]
    # convert to dataframe
    df_datastreams = pd.DataFrame(station_datastream_links)
    return df_datastreams


def load_station_fill_history(
    datastream_link: str,
    query_start: datetime,
) -> pd.DataFrame:
    """Get all observations for one datastream.

    Args:
        datastream_link: Link to the API' datastream for one station.
        query_start: Start time of the query, in UTC timezone.

    Returns:
        All data for one station.
    """
    assert query_start.tzinfo == pytz.UTC

    # create url for scraping
    query_start_str = query_start.strftime("%Y-%m-%dT%H:%M:%S.%fZ").replace(":", "%3A")
    FILTER = f"$select=phenomenonTime,result&$filter=%28phenomenonTime+gt+{query_start_str}%29"
    STATION_URL = datastream_link + "?" + FILTER

    print("load paginated station data...")
    station_results = []
    response = requests.get(STATION_URL)
    while True:
        next_url = response.json().get("@iot.nextLink")
        print(next_url)
        # Extract the data from the response
        data = response.json()["value"]
        # Append the data to the results list
        station_results += data
        # If there is no next page, break the loop
        if not response.json().get("@iot.nextLink"):
            break
        # Send the next request to the API
        response = requests.get(next_url)
    print("station scraped.")

    # select only relevant fields
    station_flat = [
        {
            "timestamp": record["phenomenonTime"],
            "result": record["result"],
        }
        for record in station_results
    ]

    # convert to dataframe
    df_station = (
        pd.DataFrame(station_flat).sort_values(by="timestamp")
        # transform timestamp to datetime
        .assign(timestamp=lambda x: pd.to_datetime(x.timestamp))
    )
    return df_station
