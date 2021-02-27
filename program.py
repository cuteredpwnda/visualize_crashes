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
def read_input(location):
    tic = time.perf_counter()
    df = pd.read_csv(location, sep=';')
    toc = time.perf_counter()
    filename = location[location.rfind('/')+1:location.rfind('.')] 
    print(f'reading the {filename} csv took {toc-tic:0.4f} seconds.')
    df.name = filename
    return df

df_2019 = read_input('data/Unfallorte2019_EPSG25832_CSV/csv/Unfallorte2019_LinRef.txt')
df_2018 = read_input('data/Unfallorte2018_EPSG25832_CSV/csv/Unfallorte2018_LinRef.txt')
df_2017 = read_input('data/Unfallorte2017_EPSG25832_CSV/csv/Unfallorte2017_LinRef.txt')

#reformat koordinates, replace , with .
def replace_commas(df):
    tic = time.perf_counter()
    for col in ['XGCSWGS84', 'YGCSWGS84']:
        df[col] = pd.to_numeric(df[col].apply(lambda x: re.sub(',' , '.', str(x))))
    toc = time.perf_counter()
    print(f'replacing all commas in {df.name} with dots took {toc-tic:0.4f} seconds.')

replace_commas(df_2019)
replace_commas(df_2018)
replace_commas(df_2017)

# create a readable column for info
def create_infocolumn(df):
    df['Info'] = 'Stunde: ' +  df['USTUNDE'].astype(str)+ ' Uhr' + '\n' +' Monat: ' +  df['UMONAT'].astype(str)  + '\n' +' Jahr: ' + df['UJAHR'].astype(str)

create_infocolumn(df_2019)
create_infocolumn(df_2018)
create_infocolumn(df_2017)

# print(df_2019['Info'])

#filter for state
class State():
    SchleswigHolstein = 1
    Hamburg = 2
    Niedersachsen = 3
    Bremen = 4
    NordrheinWestfalen = 5
    Hessen = 6
    RheinlandPfalz = 7
    BadenWürttemberg = 8
    Bayern = 9
    Saarland = 10
    Berlin = 11
    Brandenburg = 12
    MecklenburgVorpommern = 13
    Sachsen = 14
    SachsenAnhalt = 15
    Thüringen = 16

def filter_state(state_name_nochars, df):
    tic = time.perf_counter()
    df_filtered = df.loc[df['ULAND'] == int(state_name_nochars)]
    toc = time.perf_counter()
    print(f'filtering for {state_name_nochars} took {toc-tic:0.4f} seconds.')
    df_filtered.name = df.name + '_state'
    return df_filtered

# get nrw values
df_2019_nrw = filter_state(State.NordrheinWestfalen, df_2019)


#filter for dortmund, AGS = 05 9 13 000 BL Regbez Kreis Gemeinde
def filter_town_ags(ags, df):
    tic = time.perf_counter()
    df_filtered = df.loc[(df['UREGBEZ'] == int(ags[1])) & (df['UKREIS'] == int(ags[2:4]))]
    toc = time.perf_counter()
    print(f'filtering for {ags} took {toc-tic:0.4f} seconds.')
    df_filtered.name = df.name + '_town'
    return df_filtered

df_2019_nrw_dortmund = filter_town_ags('5913000', df_2019_nrw)

# only bikes
def filter_bike(df):
    tic = time.perf_counter()
    df_filtered = df.loc[df['IstRad'] == 1]
    toc = time.perf_counter()
    print(f'filtering for bikes took {toc-tic:0.4f} seconds.')
    df_filtered.name = df.name + '_bike'
    return df_filtered

df_2019_nrw_dortmund_bike = filter_bike(df_2019_nrw_dortmund)

# find the map center
def findcenter(df, lat_name, lon_name):
    tic = time.perf_counter()
    lat_center = (df[lat_name].min()+df[lat_name].max())/2
    lon_center = (df[lon_name].min()+df[lon_name].max())/2
    toc = time.perf_counter()
    print(f'finding the map center {toc-tic:0.4f} seconds.')
    return (lat_center,lon_center)

#one is enough, no big spread
center = findcenter(df_2019_nrw_dortmund_bike, 'YGCSWGS84', 'XGCSWGS84')
print(center)

#load map
tic = time.perf_counter()
map = folium.Map(location = center, 
                tiles='openstreetmap',
                zoom_start = 11)
toc = time.perf_counter()
print(f'creating the map took {toc-tic:0.4f} seconds.')

# add all dfs to a list of dfs, tuple for color
class YearColor:
    color2019 = '009988'
    color2018 = 'EE7733'
    color2017 = 'EE3377'
    
df_list = [(df_2019_nrw_dortmund_bike, YearColor.color2019)]

# add markers
marker_cluster = MarkerCluster().add_to(map)
def add_markers(df, df_label, lat_name, lon_name, map, color, iconcolor):
    for idx, row in df.iterrows():
        popup = folium.Popup(row[df_label], max_width=450,min_width=100)
        folium.Marker(
                        location = [row[lat_name], row[lon_name]], 
                        popup=popup,
                        clustered_marker=True,
                        icon=folium.Icon(color = color, icon_color=iconcolor, icon= 'bicycle', prefix='fa')).add_to(marker_cluster)


for i in range(len(df_list)):
    tic = time.perf_counter()
    add_markers(df_list[i][0], 'Info', 'YGCSWGS84', 'XGCSWGS84', map, 'white', df_list[i][1])
    toc = time.perf_counter()
    print(f'adding clustered markers of {df_list[i][0].name} to the map took {toc-tic:0.4f} seconds.')

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
    print(df_2019_nrw_dortmund)
    print(df_2019_nrw_dortmund_bike)
    print(center)