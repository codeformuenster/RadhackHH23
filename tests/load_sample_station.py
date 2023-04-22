"""Load and plot data for one station."""

# %%
from datetime import datetime

import pytz
from matplotlib import pyplot as plt

from bike_balance.load import load_station_datastreams, load_station_fill_history

df_datastreams = load_station_datastreams()

# load for one station
datastream_link = df_datastreams.datastrem_link[0]
query_start = datetime(2023, 3, 1, tzinfo=pytz.UTC)
df_station = load_station_fill_history(datastream_link, query_start)


# plot data of one station
(
    df_station
    # create required fields
    .assign(date=lambda x: x.timestamp.dt.date)
    .assign(time=lambda x: x.timestamp.dt.time)
    .groupby("date")
    .plot(
        x="time",
        y="result",
        ax=plt.gca(),
        legend=False,
        title="Bikes at station",
        alpha=0.35,
    )
)
df_station.plot(
    x="timestamp",
    y="result",
    legend=False,
    title="Bikes at station",
    alpha=1,
)

# %%
