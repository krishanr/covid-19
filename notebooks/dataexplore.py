# %%
import csv
import pandas as pd
from pathlib import Path

# %%
project_dir = Path(__file__).resolve().parents[1]
# %%
df = pd.read_csv(project_dir / "data/raw/2020-03-13" / "all_sources_metadata_2020-03-13.csv")

# %%
df.columns
# %%
df.head(10)
# %%
import collections

collections.Counter(
    p.suffix
    for p in (project_dir / "data/raw/2020-03-13/comm_use_subset/comm_use_subset").iterdir()
)

# %%
json_file = list((project_dir / "data/raw/2020-03-13/comm_use_subset/comm_use_subset").iterdir())[0]

# %%
import json

# read file
with open(json_file, "r") as myfile:
    data = myfile.read()

# parse file
obj = json.loads(data)

print(obj)


# %%
