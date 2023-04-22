"""Load and plot data for one station."""

# %%
from datetime import datetime

import pandas as pd
import pytz

from bike_balance.load import (
    load_station_datastreams,
    load_station_fill_history,
    load_station_master_data,
)

QUERY_START = datetime(2023, 4, 20, tzinfo=pytz.UTC)

# load master data and datastreams
df_master_data = load_station_master_data()
df_datastreams = load_station_datastreams()


# %%

station_master_dfs = []

for index, row in df_datastreams.iterrows():
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

df_stations = pd.concat(station_master_dfs).sort_values(
    by=["station_name", "timestamp"],
    ignore_index=True,
)


# %% write data to csv
df_stations.rename(columns={"result": "bikes_available"}).to_csv(
    "data/stations_fill.csv", index=False
)

# %%


# plot data of one station
# (
#     df_station
#     # create required fields
#     .assign(date=lambda x: x.timestamp.dt.date)
#     .assign(time=lambda x: x.timestamp.dt.time)
#     .groupby("date")
#     .plot(
#         x="time",
#         y="result",
#         ax=plt.gca(),
#         legend=False,
#         title="Bikes at station",
#         alpha=0.35,
#     )
# )
df_station.plot(
    x="timestamp",
    y="result",
    legend=False,
    title="Bikes at station",
    alpha=1,
)

# %%
