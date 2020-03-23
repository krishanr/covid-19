# %%
import csv
from pathlib import Path
from datetime import datetime, timedelta

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
import shutil

# %%
project_dir = Path(__file__).resolve().parents[1]
data_dir = project_dir / "data/raw/COVID-19"

# %%
# Let's get the latest data from the John Hopkins github repo.
covid_dir_lastmod_utc = datetime.fromtimestamp(data_dir.stat().st_mtime)+ timedelta(hours=4)
# TODO: does this give the latest data?
if covid_dir_lastmod_utc.date() < datetime.utcnow().date():
    shutil.rmtree(str(data_dir))
    ! git clone "https://github.com/CSSEGISandData/COVID-19"
    shutil.move(str(project_dir / "notebooks/COVID-19"), str(project_dir / "data/raw"))

# %%
# Let's do some basic data exploration.
df = pd.read_csv(
    data_dir
    / "csse_covid_19_data"
    / "csse_covid_19_time_series"
    / "time_series_19-covid-Confirmed.csv"
)
df

# %%
# any missing data?
total = df.isnull().sum().sort_values(ascending=False)
percent = (df.isnull().sum()/df.isnull().count() * 100).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis = 1, keys=["Total", "Percent"])
print(missing_data.shape)
missing_data.head(20)
# %%
region = "Canada" #Try China, Italy, Iran, Canada etc.
region_df = df.loc[df["Country/Region"] == region]
region_df

# %%
# Visualize cases in Canada using folium
# Idea and code from Geospatial data processing presentation at PyCon 2019.
# See here: https://www.youtube.com/watch?v=SXW_b_lZRtU&amp=&index=9
import folium
geometry = [Point(pos) for pos in zip(region_df["Lat"], region_df["Long"])]
gdf = gpd.GeoDataFrame(region_df, geometry=geometry)

region_map = folium.Map(location=[0, 0], zoom_start=2)
last_column = len(region_df.columns) - 2  # subtract 2 since we added geometry
scale = 10

def add_row_to_map(row):
    lat, lng = row[2], row[3]
    case_count = row[last_column]
    try:
        name = row[0] if not (np.isnan(row[0])) else row[1]
    except: # ignore numpy throwing not a number error
        name = row[0]
    folium.CircleMarker(
        [lat, lng],
        radius=case_count / scale,
        popup=name + "<br/>" + f"Viral cases: {str(case_count)}",
        color="#3186cc",
        fill=True,
        fill_color="#3186cc",
    ).add_to(region_map)


region_df.apply(add_row_to_map, axis=1)
region_map

# %%
# Now let's create a simple graph of the cases in Canada
from matplotlib import pyplot as plt
import numpy as np

# Change row_num to move to a different province
row_num = 0
indices = range(0, len(region_df.columns[4:last_column]))
# select the non-zero cases
infections = region_df.iloc[row_num, 4:last_column].values
non_zero_infections = infections[np.nonzero(infections)[0]]
non_zero_infections = non_zero_infections.astype(float) # np.log complains otherwise :(

plt.figure()
plt.plot(indices, infections)
plt.xlabel("Days")
plt.ylabel("Confirmed cases")
# TODO: region here should be replaced by the province when possible
plt.title(f"Confirmed cases in {region}")

# %%
# plot the non-zero cases and the log on the same graph
non_zero_indices = range(0, len(non_zero_infections))
plt.figure()
plt.subplot(211)
plt.plot(non_zero_indices, non_zero_infections, 'r--')
plt.xlabel("Days")
plt.ylabel("Confirmed cases")
plt.title(f"Non-zero confirmed cases in {region}")
plt.subplot(212)
plt.plot(non_zero_indices, np.log(non_zero_infections), 'bs')
plt.xlabel("Days")
plt.ylabel("Log confirmed cases")
plt.title(f"Log-scale of confirmed cases in {region}")

# Adjust the subplot layout
plt.subplots_adjust(top=1.25, bottom=0.05,hspace=0.5)
plt.show()


# %%
