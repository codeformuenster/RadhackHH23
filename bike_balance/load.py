"""Load poetry file."""

# %%
import json
from pathlib import Path

import requests

URL = "https://iot.hamburg.de/v1.0/Datastreams?$count=true&$filter=properties/serviceName%20eq%20%27HH_STA_StadtRad%27%20and%20properties/layerName%20eq%20%27Fahrraeder%27&$expand=Observations($select=phenomenonTime,result;$orderby=phenomenonTime%20desc;$filter=phenomenonTime%20gt%202023-04-01T00:00:00Z)"

# %% call API and parse to dict
data_raw = requests.get(URL).text
data = json.loads(data_raw)

# %% save dict to file
JSON_PATH = Path("data/data.json")
with open(JSON_PATH, "w") as f:
    json.dump(data, f)


# %%
# %%
