import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# =============================================
# CONFIGURACIÓN INICIAL (ESTILO COMO PAGINA PRINCIPAL)
# =============================================
st.set_page_config(
    page_title="Bus Routes Travel Times And Average Speed Analysis", 
    page_icon="🚍", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados (igual que la página principal)
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
    
    .section-title {
        text-align: center;
        color: #2c3e50;
        font-size: 2rem;
        margin: 2rem 0 1.5rem;
        font-weight: 600;
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
    
    .option-card {
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        background: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        border: 1px solid rgba(0,0,0,0.05);
        height: 100%;
        margin-bottom: 1.5rem;
    }
    
    .option-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        padding: 0.6rem;
        font-size: 1rem;
        transition: all 0.3s;
        border: none;
        background: linear-gradient(135deg, #3498db, #2ecc71);
        color: white;
        margin-top: auto;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
    }
    
    .dataframe {
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
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

# Contenedor principal
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# =============================================
# BOTÓN DE RETORNO Y TÍTULO
# =============================================
st.markdown('<h1 class="main-title">🚍Bus Routes Travel Times And Average Speed Analysis</h1>', unsafe_allow_html=True)

# Botón de retorno centrado
col_centered = st.columns([1, 1, 1])  # Columnas para centrar el botón
with col_centered[1]:
    if st.button("🏠 Return to Main Menu", key="btn_main_menu"):
        st.session_state.page = "Pagina_Principal.py"
        st.switch_page("Pagina_Principal.py")

# =============================================
# INTRODUCCIÓN
# =============================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="objective-box">
    <h3 style="text-align: center; color: #2c3e50;">Objective</h3>
    <p style="text-align: center;">Analysing travel time and distance between each bus stop will tell us how efficient the current bus network is and where the majority of problems might be. Furthermore, it will give the user a more accurate view of the system and how clients could react to peak usage hours.</p>
</div>
""", unsafe_allow_html=True)

# =============================================
# CARGA DE DATOS
# =============================================
agency_dbus = pd.read_csv("Datos 1/agency_dbus.csv",sep=';')
calendar_dbus = pd.read_csv("Datos 1/calendar_dbus.csv",sep=';')
routes_dbus = pd.read_csv("Datos 1/routes_dbus.csv",sep=';')
stt_dbus = pd.read_csv("Datos 1/stop_times_dbus.csv",sep=';')
stt2_dbus = pd.read_csv("Datos 1/stop_times_dbus.csv",sep=';')
st_dbus = pd.read_csv("Datos 1/stops_dbus.csv",sep=';')
tri_dbus = pd.read_csv("Datos 1/trips_dbus.csv",sep=';')
sha_dbus = pd.read_csv("Datos 1/sha_dbus.csv",sep=';')

# =============================================
# PROCESAMIENTO DE DATOS
# =============================================
# Corrección de distancias
stt_dbus['shape_dist_traveled'] = stt_dbus['shape_dist_traveled'].astype(str).str.replace(',', '.').astype(float)
stt_dbus.loc[stt_dbus['shape_dist_traveled'] < 12, 'shape_dist_traveled'] *= 1000

# Obtención del tiempo entre paradas
stt_dbus['arrival_time'] = pd.to_timedelta(stt_dbus['arrival_time'])
stt_dbus['departure_time'] = pd.to_timedelta(stt_dbus['departure_time'])
stt_dbus['time_difference'] = (stt_dbus['departure_time'] - stt_dbus['arrival_time']).dt.total_seconds()
stt_dbus['time_between_stops'] = stt_dbus['arrival_time'] - stt_dbus.groupby('trip_id')['departure_time'].shift(1)
stt_dbus['time_between_stops'] = stt_dbus['time_between_stops'].fillna(pd.Timedelta(seconds=0))
stt_dbus['time_between_stops'] = stt_dbus['time_between_stops'].dt.total_seconds()

# Relaciona el trip id con la ruta y día de la semana
df = (tri_dbus.sort_values(by=['route_id'],ascending=True))[['trip_id','route_id','service_id']]
stt_dbus = stt_dbus.merge(df[['trip_id', 'route_id','service_id']], on='trip_id', how='left')
stt_dbus = stt_dbus.drop_duplicates()

# Obtención del tiempo total de recorrido
mf = (df.groupby(by=['route_id','service_id']).size().reset_index()).rename(columns={0: 'trip_count'})
suma = stt_dbus.groupby(by=['route_id','service_id'])[['time_between_stops']].sum().reset_index()
total_travel_time = suma.merge(mf[['trip_count','route_id','service_id']], on=['route_id','service_id'], how='left')
total_travel_time['avg_travel_time'] = total_travel_time['time_between_stops'] / total_travel_time['trip_count']

# DataFrame final con estadísticas
merged_df = total_travel_time[['route_id','service_id','trip_count','avg_travel_time']]
distance_stats_per_route = stt_dbus[stt_dbus['time_between_stops']>0].groupby(by=['route_id', 'service_id'])['time_between_stops'].agg(
    avg_time='mean',
    median_time='median',
    std_time='std',
    min_time='min',
    max_time='max',
    count_time='count'
).reset_index()
merged_df = merged_df.merge(distance_stats_per_route, on=['route_id', 'service_id'], how='left')

# DataFrame con datos relevantes
df_final = stt_dbus[['route_id', 'service_id', 'trip_id', 'stop_id','stop_sequence','time_between_stops','shape_dist_traveled']]
df_final['distance_between_stops'] = (df_final['shape_dist_traveled']-df_final.groupby('trip_id')['shape_dist_traveled'].shift(1))
df_final['distance_between_stops'] = df_final['distance_between_stops'].fillna(0)
df_final['avg_speed'] = df_final['distance_between_stops']/df_final['time_between_stops']
df_final['avg_speed'] = df_final['avg_speed'].fillna(0)
df_final.loc[df_final['time_between_stops'] == 0, ['avg_speed', 'distance_between_stops']] = 0

speed_stats_per_route = df_final[df_final['avg_speed'] > 0].groupby(['route_id', 'service_id'])['avg_speed'].agg(
    avg_speed='mean',
    median_speed='median',
    std_speed='std',
    min_speed='min',
    max_speed='max',
    count_speed='count'
).reset_index()

merged_df = merged_df.merge(speed_stats_per_route, on=['route_id', 'service_id'], how='left')

# =============================================
# VISUALIZACIÓN DE DATOS
# =============================================

# Data Preview 0
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align: center;">📋 1. Data Preview</h4>', unsafe_allow_html=True)
with st.expander("🔍 Data visualization (First 50 Rows)"):
    st.dataframe(df_final.head(50), use_container_width=True)

# Data Preview 1
with st.expander("📊 Descriptive statistics (First 50 Rows)"):
    st.dataframe(merged_df.head(50), use_container_width=True)

# Gráfico interactivo
st.markdown("""<div style='height: 50px;'></div>""", unsafe_allow_html=True)
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align: center;">📈 2. Route Data Visualization</h4>', unsafe_allow_html=True)

# Service label mapping
service_labels = {
    1840: "Weekdays (Mon–Thu)",
    1841: "Friday only",
    1842: "Saturday only",
    1843: "Sunday only"
}
label_to_id = {v: k for k, v in service_labels.items()}

# Controles del gráfico
col1, col2 = st.columns(2)
with col1:
    route_ids = df_final["route_id"].unique()
    selected_route = st.selectbox("Select Route ID", route_ids)

    variables = ["time_between_stops", "avg_speed"]
    selected_variable = st.selectbox("Select Variable", variables)

with col2:
    # Use labels instead of raw service_ids
    dynamic_service_ids = df_final[df_final["route_id"] == selected_route]["service_id"].unique()
    dynamic_label_options = [service_labels[sid] for sid in dynamic_service_ids if sid in service_labels]

    selected_labels = st.multiselect("Select Service Types", options=dynamic_label_options, default=dynamic_label_options[:3])
    selected_services = [label_to_id[label] for label in selected_labels]

    dynamic_stop_ids = df_final[df_final["route_id"] == selected_route]["stop_id"].unique()
    selected_stops = st.multiselect("Select Stop IDs", dynamic_stop_ids, default=dynamic_stop_ids[:5])

# Filtrar datos
filtered_df = df_final[
    (df_final["route_id"] == selected_route) &
    (df_final["service_id"].isin(selected_services)) &
    (df_final["stop_id"].isin(selected_stops)) &
    (df_final[selected_variable] > 0)
]


# Crear gráfico (boxplot con etiquetas legibles)
if not filtered_df.empty:
    # Add label column to DataFrame
    filtered_df["service_label"] = filtered_df["service_id"].map(service_labels)

    title = f"Distribution of {selected_variable} by Service Type and Stop ID for Route ID {selected_route}"
    fig = px.box(
        filtered_df,
        x="service_label",  # Use the new label column
        y=selected_variable,
        color="stop_id",
        title=title,
        labels={
            "service_label": "Service Type",
            selected_variable: selected_variable,
            "stop_id": "Stop ID"
        }
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No data available for the selected filters.")

# =============================================
# ANÁLISIS ADICIONAL 
# =============================================
st.markdown("""<div style='height: 50px;'></div>""", unsafe_allow_html=True)
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align: center;">📌 3. Additional Analysis</h4>', unsafe_allow_html=True)

# Procesamiento de datos adicional
df_2 = (tri_dbus.sort_values(by=['route_id'],ascending=True))[['trip_id','route_id','service_id']]
stt2_dbus['arrival_time'] = pd.to_timedelta(stt2_dbus['arrival_time'])
stt2_dbus['departure_time'] = pd.to_timedelta(stt2_dbus['departure_time'])
stt2_dbus['time_difference'] = (stt2_dbus['departure_time'] - stt2_dbus['arrival_time']).dt.total_seconds()
stt2_dbus['time_between_stops'] = stt2_dbus['arrival_time'] - stt2_dbus.groupby('trip_id')['departure_time'].shift(1)
stt2_dbus['time_between_stops'] = stt2_dbus['time_between_stops'].fillna(pd.Timedelta(seconds=0))
stt2_dbus['time_between_stops'] = stt2_dbus['time_between_stops'].dt.total_seconds()
stt2_dbus = stt2_dbus.merge(df_2[['trip_id', 'route_id', 'service_id']], on='trip_id', how='left')

# Filtrado por días de semana/fin de semana
stt2_dbus_weekdays = stt2_dbus[stt2_dbus['service_id'].isin([1840, 1841])]
stt2_dbus_weekends = stt2_dbus[stt2_dbus['service_id'].isin([1842, 1843])]

# Resumen de tiempos
trip_time_summary_weekdays = stt2_dbus_weekdays.groupby('trip_id')['time_between_stops'].sum().reset_index()
trip_time_summary_weekends = stt2_dbus_weekends.groupby('trip_id')['time_between_stops'].sum().reset_index()

trip_time_summary_weekdays = trip_time_summary_weekdays.merge(stt2_dbus_weekdays[['trip_id', 'route_id', 'service_id']].drop_duplicates(), on='trip_id', how='left')
trip_time_summary_weekends = trip_time_summary_weekends.merge(stt2_dbus_weekends[['trip_id', 'route_id', 'service_id']].drop_duplicates(), on='trip_id', how='left')

max_shape_dist_weekdays = stt2_dbus_weekdays.groupby('trip_id')['shape_dist_traveled'].max().reset_index()
max_shape_dist_weekends = stt2_dbus_weekends.groupby('trip_id')['shape_dist_traveled'].max().reset_index()

trip_time_summary_weekdays = trip_time_summary_weekdays.merge(max_shape_dist_weekdays, on='trip_id', how='left')
trip_time_summary_weekends = trip_time_summary_weekends.merge(max_shape_dist_weekends, on='trip_id', how='left')

trip_time_summary_weekdays.columns = ['trip_id', 'total_time_between_stops', 'route_id', 'service_id', 'max_shape_dist_traveled']
trip_time_summary_weekends.columns = ['trip_id', 'total_time_between_stops', 'route_id', 'service_id', 'max_shape_dist_traveled']

total_trip_time_summary = pd.concat([trip_time_summary_weekdays, trip_time_summary_weekends])

# Creación del DataFrame final
selected_rows = []
for index, row in total_trip_time_summary.iterrows():
    matching_rows = total_trip_time_summary[
        (total_trip_time_summary['route_id'] == row['route_id']) &
        (total_trip_time_summary['max_shape_dist_traveled'] == row['max_shape_dist_traveled']) &
        (total_trip_time_summary['service_id'] != row['service_id'])
    ]
    if not matching_rows.empty:
        selected_rows.append(row.to_dict())
        selected_rows.extend(matching_rows.to_dict(orient='records'))

new_trip_time_summary = pd.DataFrame(selected_rows)
new_trip_time_summary.drop_duplicates(inplace=True)

aggregated_trip_time_summary = new_trip_time_summary.groupby(['route_id', 'max_shape_dist_traveled', 'service_id']).agg(
    duracion_media=('total_time_between_stops', 'mean'),
    variance=('total_time_between_stops', 'var'),
    std_dev=('total_time_between_stops', 'std'),
    min_time=('total_time_between_stops', 'min'),
    max_time=('total_time_between_stops', 'max'),
    median_time=('total_time_between_stops', 'median')
).reset_index()

aggregated_trip_time_summary['variance'].fillna(0, inplace=True)
aggregated_trip_time_summary['std_dev'].fillna(0, inplace=True)

# Mostrar resultados finales
with st.expander("📌 View Aggregated Trip Time Summary (First 50 Rows)"):
    st.dataframe(aggregated_trip_time_summary.head(50), use_container_width=True)

# Cerrar contenedor principal
st.markdown('</div>', unsafe_allow_html=True)