import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import utm
import re
import folium
from folium.plugins import MarkerCluster

#read the data
df_2019 = pd.read_csv('data/Unfallorte2019_EPSG25832_CSV/csv/Unfallorte2019_LinRef.txt', sep=';')

#reformat koordinates, replace , with .
for col in ['XGCSWGS84', 'YGCSWGS84']:
    df_2019[col] = pd.to_numeric(df_2019[col].apply(lambda x: re.sub(',' , '.', str(x))))
    

#print(df_2019)

#filter for nrw
df_2019_nrw = df_2019.loc[df_2019['ULAND'] == 5 ]


#filter for dortmund, AGS = 05 9 13 000 BL Regbez Kreis Gemeinde
df_2019_dortmund = df_2019_nrw.loc[(df_2019_nrw['UREGBEZ'] == 9) & (df_2019_nrw['UKREIS'] == 13)]


# only bikes
df_2019_dortmund_bike = df_2019_dortmund.loc[df_2019_dortmund['IstRad'] == 1]
#

# find the map center
def findcenter(df, lat_name, lon_name):
    lat_center = (df[lat_name].min()+df[lat_name].max())/2
    lon_center = (df[lon_name].min()+df[lon_name].max())/2
    return (lat_center,lon_center)

center = findcenter(df_2019_dortmund_bike, 'YGCSWGS84', 'XGCSWGS84')

#load map
map = folium.Map(location = center, 
                tiles='openstreetmap',
                zoom_start = 11)

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

add_markers(df_2019_dortmund_bike, 'UART', 'YGCSWGS84', 'XGCSWGS84', map, 'white', '009988')

#save map as html
map.save("bikecrashes.html")

#debugging prints:
debug = False
if debug == True:
    print((df_2019_nrw['UREGBEZ']))
    print((df_2019_nrw['UKREIS']))
    print(df_2019_dortmund)
    print(df_2019_dortmund_bike)
    print(center)