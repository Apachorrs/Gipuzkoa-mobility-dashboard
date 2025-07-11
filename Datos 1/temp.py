# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Cargar los datos
agency_dbus = pd.read_csv("agency_dbus.csv",sep=';')
calendar_dbus = pd.read_csv("calendar_dbus.csv",sep=';')
routes_dbus = pd.read_csv("routes_dbus.csv",sep=';')
stt_dbus = pd.read_csv("stop_times_dbus.csv",sep=';')
stt2_dbus = pd.read_csv("stop_times_dbus.csv",sep=';')
st_dbus = pd.read_csv("stops_dbus.csv",sep=';')
tri_dbus = pd.read_csv("trips_dbus.csv",sep=';')
sha_dbus = pd.read_csv("sha_dbus.csv",sep=';')

# Lista de coordenadas de los 20 marcadores en Donostia (coordenadas ficticias cercanas al centro de la ciudad)

coordenadas= st_dbus[['stop_id','stop_name',"stop_lat","stop_lon"]]

#--------------------------------------------------------------------------------#
#correccion de un problema al leer las distancias, donde se interpretaba por defecto 900 m como 0.9
# Replace commas with dots and convert to float
stt_dbus['shape_dist_traveled'] = stt_dbus['shape_dist_traveled'].astype(str).str.replace(',', '.').astype(float)

# Multiply values lower than a threshold (e.g., 12) by 1000 to fix scaling issues
stt_dbus.loc[stt_dbus['shape_dist_traveled'] < 12, 'shape_dist_traveled'] *= 1000
#--------------------------------------------------------------------------------#

#Obtencion del tiempo entre paradas y el tiempo en la parada#
# Convert time columns to timedelta format
stt_dbus['arrival_time'] = pd.to_timedelta(stt_dbus['arrival_time'])
stt_dbus['departure_time'] = pd.to_timedelta(stt_dbus['departure_time'])

# Compute the time difference in seconds
stt_dbus['time_difference'] = (stt_dbus['departure_time'] - stt_dbus['arrival_time']).dt.total_seconds()

# Calculate time between stops within the same trip
stt_dbus['time_between_stops'] = stt_dbus['arrival_time'] - stt_dbus.groupby('trip_id')['departure_time'].shift(1)
# Fill the first stop of each trip with NaT since it has no previous stop
stt_dbus['time_between_stops'] = stt_dbus['time_between_stops'].fillna(pd.Timedelta(seconds=0))
# Convert to seconds for easier analysis
stt_dbus['time_between_stops'] = stt_dbus['time_between_stops'].dt.total_seconds()

#--------------------------------------------------------------------------------#

##Relaciona el trip id con que ruta es y con el dia de la semana

df = (tri_dbus.sort_values(by=['route_id'],ascending=True))[['trip_id','route_id','service_id']]
duplicates = df[df.duplicated(keep=False)]

# Merge stt_dbus with df to be able to connect trip id with its route and service
stt_dbus = stt_dbus.merge(df[['trip_id', 'route_id','service_id']], on='trip_id', how='left')
stt_dbus = stt_dbus.drop_duplicates()

#--------------------------------------------------------------------------------#

#obtencion del tiempo que tarda en completarse un recorrido

#------ Count of route number by service id(day of the week)-----------#
mf=(df.groupby(by=['route_id','service_id']).size().reset_index()).rename(columns={0: 'trip_count'})
# obtencion del tiempo total de recorrido de los buses de cada ruta dividos por dia de operacion
suma=stt_dbus.groupby(by=['route_id','service_id'])[['time_between_stops']].sum().reset_index()
total_travel_time=suma.merge(mf[['trip_count','route_id','service_id']], on=['route_id','service_id'], how='left')
total_travel_time['avg_travel_time']=total_travel_time['time_between_stops'] /total_travel_time['trip_count']


# se obtiene el tiempo promedio que tarda en completarse un recorrido
merged_df = total_travel_time[['route_id','service_id','trip_count','avg_travel_time']]

distance_stats_per_route = stt_dbus[stt_dbus['time_between_stops']>0].groupby(by=['route_id', 'service_id'])['time_between_stops'].agg(
    avg_time='mean',
    median_time='median',
    std_time='std',
    min_time='min',
    max_time='max',
    count_time='count'  # Number of records considered
).reset_index()

# Merge distance statistics with merged_df
merged_df = merged_df.merge(distance_stats_per_route, on=['route_id', 'service_id'], how='left')

#----------generacion de un nuevo data frame con los datos relevantes------------#
#Grouping valuable columns for next work
df_final = stt_dbus[['route_id', 'service_id', 'trip_id','arrival_time', 'departure_time','stop_id','stop_sequence','time_between_stops','shape_dist_traveled']]

#distancia entre las paradas
#similar than when getting time between stops, the accumulated distance till the stop in the row- the previous accumulated distance
df_final['distance_between_stops']=(df_final['shape_dist_traveled']-df_final.groupby('trip_id')['shape_dist_traveled'].shift(1))
#change Na to 0
df_final['distance_between_stops'] = df_final['distance_between_stops'].fillna(0)
#--------------------------------------------------------------------------------#

#obtencion de la velocidad promedio durante en el tramo entre cada parada---------#
#velocidad en m/s
#getting average speed from last stop(previous row) till this stop(this row)
df_final['avg_speed']=df_final['distance_between_stops']/df_final['time_between_stops']
#changing Na to 0
df_final['avg_speed'] = df_final['avg_speed'].fillna(0)

df_final.loc[df_final['time_between_stops'] == 0, ['avg_speed', 'distance_between_stops']] = 0

speed_stats_per_route = df_final[df_final['avg_speed'] > 0].groupby(['route_id', 'service_id'])['avg_speed'].agg(
    avg_speed='mean',
    median_speed='median',
    std_speed='std',
    min_speed='min',
    max_speed='max',
    count_speed='count'  # Cantidad de registros considerados
).reset_index()

merged_df = merged_df.merge(speed_stats_per_route, on=['route_id', 'service_id'], how='left')

df3=df_final[['route_id','service_id','stop_id']]

df3_grouped = df3.groupby('stop_id').agg({
    'route_id': lambda x: list(set(x))  # Quitamos duplicados y convertimos a lista
}).reset_index()
df_result = coordenadas.merge(df3_grouped, on='stop_id', how='left')


