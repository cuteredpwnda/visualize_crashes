import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import utm
import re
import folium
from folium.plugins import MarkerCluster
import time

#start timer
start_time = time.perf_counter()
#read the data
df_2019 = pd.read_csv('data/Unfallorte2019_EPSG25832_CSV/csv/Unfallorte2019_LinRef.txt', sep=';')
toc = time.perf_counter()
print(f'reading the csv took {toc-start_time:0.4f} seconds.')

#reformat koordinates, replace , with .
tic = time.perf_counter()
for col in ['XGCSWGS84', 'YGCSWGS84']:
    df_2019[col] = pd.to_numeric(df_2019[col].apply(lambda x: re.sub(',' , '.', str(x))))
toc = time.perf_counter()
print(f'replacing all commas with dots took {toc-tic:0.4f} seconds.')

#filter for nrw
tic = time.perf_counter()
df_2019_nrw = df_2019.loc[df_2019['ULAND'] == 5 ]
toc = time.perf_counter()
print(f'filtering for nrw took {toc-tic:0.4f} seconds.')

#filter for dortmund, AGS = 05 9 13 000 BL Regbez Kreis Gemeinde
tic = time.perf_counter()
df_2019_dortmund = df_2019_nrw.loc[(df_2019_nrw['UREGBEZ'] == 9) & (df_2019_nrw['UKREIS'] == 13)]
toc = time.perf_counter()
print(f'filtering for dortmund took {toc-tic:0.4f} seconds.')

# only bikes
tic = time.perf_counter()
df_2019_dortmund_bike = df_2019_dortmund.loc[df_2019_dortmund['IstRad'] == 1]
toc = time.perf_counter()
print(f'filtering for bikes took {toc-tic:0.4f} seconds.')

# find the map center
def findcenter(df, lat_name, lon_name):
    lat_center = (df[lat_name].min()+df[lat_name].max())/2
    lon_center = (df[lon_name].min()+df[lon_name].max())/2
    return (lat_center,lon_center)

tic = time.perf_counter()
center = findcenter(df_2019_dortmund_bike, 'YGCSWGS84', 'XGCSWGS84')
toc = time.perf_counter()
print(f'finding the center {toc-tic:0.4f} seconds.')

#load map
tic = time.perf_counter()
map = folium.Map(location = center, 
                tiles='openstreetmap',
                zoom_start = 11)
toc = time.perf_counter()
print(f'creating the map took {toc-tic:0.4f} seconds.')

# add markers
def add_markers(df, df_label, lat_name, lon_name, map, color, iconcolor):
    marker_cluster = MarkerCluster().add_to(map)
    for idx, row in df.iterrows():
        popup = folium.Popup(row[df_label], max_width=450,min_width=100)
        folium.Marker(
                        location = [row[lat_name], row[lon_name]], 
                        popup=popup,
                        clustered_marker=True,
                        icon=folium.Icon(color = color, icon_color=iconcolor, icon= 'bicycle', prefix='fa')).add_to(marker_cluster)

tic = time.perf_counter()
add_markers(df_2019_dortmund_bike, 'UART', 'YGCSWGS84', 'XGCSWGS84', map, 'white', '009988')
toc = time.perf_counter()
print(f'adding clustered markers to the map took {toc-tic:0.4f} seconds.')

#save map as html
tic = time.perf_counter()
map.save("bikecrashes.html")
toc = time.perf_counter()
print(f'saving the map took {toc-tic:0.4f} seconds.')

tic = time.perf_counter()
print(f'everything took {toc-start_time:0.4f} seconds.')
#debugging prints:
debug = False
if debug == True:
    print((df_2019_nrw['UREGBEZ']))
    print((df_2019_nrw['UKREIS']))
    print(df_2019)
    print(df_2019_dortmund)
    print(df_2019_dortmund_bike)
    print(center)