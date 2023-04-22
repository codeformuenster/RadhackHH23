"""Load and plot data for one station."""

# %%
from datetime import datetime, tzinfo

import numpy as np
import pandas as pd
import pytz
import seaborn as sns
from matplotlib import pyplot

from bike_balance.load import (
    load_station_datastreams,
    load_station_fill_history,
    load_station_master_data,
)

QUERY_START = datetime(2023, 4, 12, tzinfo=pytz.UTC)


# load master data and datastream(s)
df_master_data = load_station_master_data()
df_datastreams = load_station_datastreams()


# %% filter down to relevant station
FILTER_NAME = "Heidi-Kabel-Platz"
filter_uuid = df_master_data.query(
    f"station_name.str.contains('{FILTER_NAME}')"
).station_uuid.values[0]

df_datastreams_filtered = df_datastreams.query("station_uuid == @filter_uuid")

# %%

station_master_dfs = []

for index, row in df_datastreams_filtered.iterrows():
    print(f"loading data for index {index} of {len(df_datastreams)} stations...")

    # load fill data for one station
    station_datastream_link = df_datastreams.datastrem_link[index]
    station_uuid = df_datastreams.station_uuid[index]

    if station_uuid not in df_master_data.station_uuid.values:
        print(f"{station_uuid} not in master data. Skipping {station_uuid}.")
        continue

    df_station = load_station_fill_history(
        station_datastream_link=station_datastream_link,
        station_uuid=station_uuid,
        query_start=QUERY_START,
    )

    df_station_master = df_station.merge(
        right=df_master_data,
        on="station_uuid",
    )
    station_master_dfs.append(df_station_master)

df_stations = (
    pd.concat(station_master_dfs)
    .sort_values(
        by=["station_name", "timestamp"],
        ignore_index=True,
    )
    .rename(columns={"result": "bikes_available"})
)


# %% write data to csv
df_stations.to_csv("data/stations_fill.csv", index=False)

# %% plot data of one station


plot_data = (
    df_stations
    # create fields time and date
    .assign(
        hour=lambda x: (x.timestamp - pd.to_datetime(x.timestamp.dt.date, utc=True))
        / np.timedelta64(1, "h"),
        date=lambda x: x.timestamp.dt.date,
    )
)

plot_data.plot.scatter(
    x="hour",
    y="bikes_available",
    legend=False,
    title="Bikes at station",
    alpha=0.1,
)
# add title
pyplot.title("Bikes at Hauptbahnhof (Heidi-Kabel-Platz)")

# %% plot a 2d histogram with seaborn
sns.histplot(
    data=plot_data,
    x="hour",
    y="bikes_available",
    bins=30,
    cbar=True,
    cbar_kws={"label": "Number of observations"},
    legend=False,
)

# %% plot single station

df_stations.plot(
    x="timestamp",
    y="bikes_available",
    legend=False,
    title="Bikes at station",
    alpha=1,
)
# add title
pyplot.title("Bikes at Hauptbahnhof (Heidi-Kabel-Platz)")

# %%
