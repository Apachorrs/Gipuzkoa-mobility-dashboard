import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from folium import PolyLine
from geopy.distance import geodesic
from datetime import time
from branca.element import Template, MacroElement

# =============================================
# CONFIGURACIÓN INICIAL
# =============================================
st.set_page_config(
    page_title="Interactive Map", 
    page_icon="🚌", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    .main-title {
        text-align: center;
        color: #2c3e50;
        font-size: 3.5rem;
        margin-bottom: 1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .section-divider {
        border-top: 1px solid #e0e0e0;
        margin: 2rem 0;
        opacity: 0.6;
    }
    .subsection-divider {
        border-top: 1px solid #f0f0f0;
        margin: 1.5rem 0;
        opacity: 0.4;
    }
    .objective-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

# =============================================
# TÍTULO Y BOTÓN DE RETORNO
# =============================================
st.markdown('<h1 class="main-title">🗺️ Interactive Map</h1>', unsafe_allow_html=True)
col_centered = st.columns([1, 1, 1])
with col_centered[1]:
    if st.button("🏠 Return to Main Menu", key="btn_main_menu"):
        st.session_state.page_to_load = "Pagina_Principal.py"
        st.switch_page("Pagina_Principal.py")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# =============================================
# CARGA Y PROCESAMIENTO DE DATOS
# =============================================
@st.cache_data
def load_data():
    agency_dbus = pd.read_csv("Datos 1/agency_dbus.csv", sep=';')
    calendar_dbus = pd.read_csv("Datos 1/calendar_dbus.csv", sep=';')
    routes_dbus = pd.read_csv("Datos 1/routes_dbus.csv", sep=';')
    stt_dbus = pd.read_csv("Datos 1/stop_times_dbus.csv", sep=';')
    st_dbus = pd.read_csv("Datos 1/stops_dbus.csv", sep=';')
    tri_dbus = pd.read_csv("Datos 1/trips_dbus.csv", sep=';')
    sha_dbus = pd.read_csv("Datos 1/sha_dbus.csv", sep=';')
    return agency_dbus, calendar_dbus, routes_dbus, stt_dbus, st_dbus, tri_dbus, sha_dbus

agency_dbus, calendar_dbus, routes_dbus, stt_dbus, st_dbus, tri_dbus, sha_dbus = load_data()

stt_dbus['shape_dist_traveled'] = stt_dbus['shape_dist_traveled'].astype(str).str.replace(',', '.').astype(float)
stt_dbus.loc[stt_dbus['shape_dist_traveled'] < 12, 'shape_dist_traveled'] *= 1000

# Unión de datos
stt_dbus = stt_dbus.merge(tri_dbus[['trip_id', 'route_id', 'service_id', 'direction_id', 'shape_id']], on='trip_id', how='left').drop_duplicates()
stt_dbus['arrival_time'] = pd.to_timedelta(stt_dbus['arrival_time'])
stt_dbus['departure_time'] = pd.to_timedelta(stt_dbus['departure_time'])
stt_dbus['time_between_stops'] = stt_dbus['arrival_time'] - stt_dbus.groupby('trip_id')['departure_time'].shift(1)
stt_dbus['time_between_stops'] = stt_dbus['time_between_stops'].fillna(pd.Timedelta(seconds=0)).dt.total_seconds()

# Crear df_final
stt_dbus['distance_between_stops'] = stt_dbus['shape_dist_traveled'] - stt_dbus.groupby('trip_id')['shape_dist_traveled'].shift(1)
stt_dbus['distance_between_stops'] = stt_dbus['distance_between_stops'].fillna(0)
stt_dbus['avg_speed'] = stt_dbus['distance_between_stops'] / stt_dbus['time_between_stops']
stt_dbus['avg_speed'] = stt_dbus['avg_speed'].fillna(0)
stt_dbus.loc[stt_dbus['time_between_stops'] == 0, ['avg_speed', 'distance_between_stops']] = 0

df_final = stt_dbus[['route_id', 'service_id', 'trip_id', 'direction_id', 'shape_id',
                     'arrival_time', 'stop_id', 'stop_sequence', 'time_between_stops', 'shape_dist_traveled',
                     'distance_between_stops', 'avg_speed']]

# Agrupar rutas por parada
df3 = df_final[['route_id', 'stop_id']]
df3_grouped = df3.groupby('stop_id').agg({'route_id': lambda x: list(set(x))}).reset_index()
df_result = st_dbus[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']].merge(df3_grouped, on='stop_id', how='left')

# =============================================
# INTERFAZ Y FILTROS
# =============================================
st.markdown("""
<div class="objective-box">
    <h3 style="text-align: center; color: #2c3e50;">Objective</h3>
    <p style="text-align: center;">Interactive heat map that shows average speed between consecute stops to detect delays and bottlenecks.</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="subsection-divider"></div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 3])

with col1:
    rutas_validas = df_final["route_id"].dropna().astype(str)
    rutas_validas = rutas_validas[rutas_validas.str.isnumeric() & (rutas_validas.astype(int) <= 100)]
    route_id = st.selectbox("🚏 Select a route:", ["All"] + sorted(rutas_validas.unique(), key=lambda x: int(x)))

with col2:
    hora_inicio, hora_fin = st.slider(
        "⏰ Select time range:",
        min_value=time(0, 0),
        max_value=time(23, 59),
        value=(time(7, 0), time(10, 0)),
        format="HH:mm"
    )

st.markdown('<div class="subsection-divider"></div>', unsafe_allow_html=True)

# =============================================
# FILTRADO DE DATOS
# =============================================
df_final["arrival_time_only"] = pd.to_datetime(df_final["arrival_time"].astype(str)).dt.time

if route_id != "All":
    df_filtrado = df_final[(df_final["route_id"].astype(str) == route_id) &
                           (df_final["arrival_time_only"] >= hora_inicio) &
                           (df_final["arrival_time_only"] <= hora_fin)]
else:
    df_filtrado = df_final[(df_final["arrival_time_only"] >= hora_inicio) &
                           (df_final["arrival_time_only"] <= hora_fin)]

segment_speeds = df_filtrado[df_filtrado["stop_sequence"] > 1].copy()
segment_speeds["prev_stop_id"] = segment_speeds.groupby('trip_id')['stop_id'].shift(1)
segment_speeds = segment_speeds.dropna(subset=["prev_stop_id"])
segment_avg = segment_speeds.groupby(['shape_id', 'prev_stop_id', 'stop_id'])['avg_speed'].mean().reset_index()

# =============================================
# CREACIÓN DEL MAPA
# =============================================
def get_color(speed):
    if speed < 1.2:
        return 'red'
    elif speed < 2:
        return 'orangered'
    elif speed < 3:
        return 'orange'
    elif speed < 4:
        return 'gold'
    elif speed < 5:
        return 'yellowgreen'
    elif speed < 6.5:
        return 'lightgreen'
    elif speed < 9:
        return 'green'
    else:
        return 'darkgreen'

mapa = folium.Map(location=[43.3197, -1.9813], zoom_start=14)

if route_id == "All":
    for _, row in df_result.iterrows():
        folium.Marker(
            location=[row["stop_lat"], row["stop_lon"]],
            popup=f"{row['stop_name']}<br>Routes: {', '.join(map(str, row['route_id'])) if isinstance(row['route_id'], list) else 'N/A'}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(mapa)
else:
    stops_in_route = df_result[df_result['route_id'].apply(lambda x: str(route_id) in list(map(str, x)) if isinstance(x, list) else False)]
    for _, row in stops_in_route.iterrows():
        folium.Marker(
            location=[row["stop_lat"], row["stop_lon"]],
            popup=f"{row['stop_name']}<br>Routes: {', '.join(map(str, row['route_id'])) if isinstance(row['route_id'], list) else 'N/A'}",
            icon=folium.Icon(color="red", icon="info-sign")
        ).add_to(mapa)

    for _, row in segment_avg.iterrows():
        shape_id = row['shape_id']
        stop1 = st_dbus[st_dbus['stop_id'] == row['prev_stop_id']][['stop_lat', 'stop_lon']].values
        stop2 = st_dbus[st_dbus['stop_id'] == row['stop_id']][['stop_lat', 'stop_lon']].values
        if len(stop1) == 0 or len(stop2) == 0:
            continue
        coord1, coord2 = stop1[0], stop2[0]
        shape_points = sha_dbus[sha_dbus['shape_id'] == shape_id].sort_values('shape_pt_sequence')
        shape_coords = shape_points[['shape_pt_lat', 'shape_pt_lon']].values.tolist()
        idx1 = min(range(len(shape_coords)), key=lambda i: geodesic(shape_coords[i], coord1).meters)
        idx2 = min(range(len(shape_coords)), key=lambda i: geodesic(shape_coords[i], coord2).meters)
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        segment_coords = shape_coords[idx1:idx2+1]
        if len(segment_coords) >= 2:
            PolyLine(
                locations=segment_coords,
                color=get_color(row['avg_speed']),
                weight=6,
                tooltip=f"Avg Speed: {row['avg_speed']:.2f} m/s"
            ).add_to(mapa)

legend_html = """
{% macro html() %}
<div style="position: fixed; top: 15px; right: 15px; width: 270px; height: auto; z-index: 9999;
background-color: white; padding: 10px; border: 2px solid grey; border-radius: 10px; font-size: 14px;
color: black; box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
<b>Velocidad promedio</b><br>
<small>(m/s | km/h)</small><br>
<div style="margin-top:5px;">
<i style="background:red;width:18px;height:18px;float:left;margin-right:8px;opacity:0.7;"></i> < 1.2 | < 4.3<br>
<i style="background:orangered;width:18px;height:18px;float:left;margin-right:8px;opacity:0.7;"></i> 1.2 - 2 | 4.3 - 7.2<br>
<i style="background:orange;width:18px;height:18px;float:left;margin-right:8px;opacity:0.7;"></i> 2 - 3 | 7.2 - 10.8<br>
<i style="background:gold;width:18px;height:18px;float:left;margin-right:8px;opacity:0.7;"></i> 3 - 4 | 10.8 - 14.4<br>
<i style="background:yellowgreen;width:18px;height:18px;float:left;margin-right:8px;opacity:0.7;"></i> 4 - 5 | 14.4 - 18.0<br>
<i style="background:lightgreen;width:18px;height:18px;float:left;margin-right:8px;opacity:0.7;"></i> 5 - 6.5 | 18.0 - 23.4<br>
<i style="background:green;width:18px;height:18px;float:left;margin-right:8px;opacity:0.7;"></i> 6.5 - 9 | 23.4 - 32.4<br>
<i style="background:darkgreen;width:18px;height:18px;float:left;margin-right:8px;opacity:0.7;"></i> > 9 | > 32.4
</div>
</div>
{% endmacro %}
"""
legend = MacroElement()
legend._template = Template(legend_html)
mapa.get_root().add_child(legend)

st_folium(mapa, use_container_width=True, height=800)
st.markdown('</div>', unsafe_allow_html=True)
