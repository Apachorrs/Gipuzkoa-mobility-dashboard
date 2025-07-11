import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# =============================================
# CONFIGURACIÓN INICIAL (ESTILO COMO PAGINA PRINCIPAL)
# =============================================
st.set_page_config(
    page_title="Bus Vs Bicycle Routes Analysis", 
    page_icon="🚌", 
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
    
    .objective-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border-left: 4px solid #3498db;
    }
    
    .bike-recommendation {
        background-color: #e3f8e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border-left: 4px solid #2ecc71;
    }
    
    .bus-recommendation {
        background-color: #fdebd0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border-left: 4px solid #f39c12;
    }
    
    .warning-box {
        background-color: #fff3cd;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        border-left: 4px solid #ffc107;
    }
    
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Contenedor principal
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# =============================================
# ENCABEZADO PRINCIPAL
# =============================================
st.markdown('<h1 class="main-title">🚍 Bus Vs Bicycle Routes Analysis 🚲</h1>', unsafe_allow_html=True)

# Botón de retorno centrado
col_centered = st.columns([1, 1, 1])
with col_centered[1]:
    if st.button("🏠 Return to Main Menu", key="btn_main_menu"):
        st.session_state.page_to_load = "Pagina_Principal.py"
        st.switch_page("Pagina_Principal.py")

# Caja de objetivo
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
with st.container():
    st.markdown("""
    <div class="objective-box">
        <h3 style="text-align: center; color: #2c3e50;">Objective</h3>
        <p style="text-align: center;">Evaluate and compare the relative efficiency of bus vs. bicycle transportation 
    for specific route segments, analyzing speed, estimated travel time, and optimal mode selection 
    based on real operational data.</p>
    </div>
    """, unsafe_allow_html=True)

# --- Carga y procesamiento de datos ---
@st.cache_data
def load_data():
    # Cargar datos originales
    agency_dbus = pd.read_csv("Datos 1/agency_dbus.csv", sep=';')
    calendar_dbus = pd.read_csv("Datos 1/calendar_dbus.csv", sep=';')
    routes_dbus = pd.read_csv("Datos 1/routes_dbus.csv", sep=';')
    stt_dbus = pd.read_csv("Datos 1/stop_times_dbus.csv", sep=';')
    st_dbus = pd.read_csv("Datos 1/stops_dbus.csv", sep=';')
    tri_dbus = pd.read_csv("Datos 1/trips_dbus.csv", sep=';')
    sha_dbus = pd.read_csv("Datos 1/sha_dbus.csv", sep=';')
    
    # Procesamiento de stop_times
    stt_dbus['shape_dist_traveled'] = stt_dbus['shape_dist_traveled'].astype(str).str.replace(',', '.').astype(float)
    stt_dbus.loc[stt_dbus['shape_dist_traveled'] < 12, 'shape_dist_traveled'] *= 1000
    
    # Convertir tiempos y calcular diferencias
    stt_dbus['arrival_time'] = pd.to_timedelta(stt_dbus['arrival_time'])
    stt_dbus['departure_time'] = pd.to_timedelta(stt_dbus['departure_time'])
    
    # Calcular distancia y tiempo entre paradas consecutivas
    stt_dbus['dist_between_stops'] = stt_dbus.groupby('trip_id')['shape_dist_traveled'].diff()
    stt_dbus['time_between_stops'] = stt_dbus.groupby('trip_id')['arrival_time'].diff().dt.total_seconds()
    
    # Calcular velocidad (km/h) entre paradas
    stt_dbus['speed_kmh'] = (stt_dbus['dist_between_stops'] / 1000) / (stt_dbus['time_between_stops'] / 3600)
    
    # Unir con información de rutas y paradas
    stt_dbus = stt_dbus.merge(tri_dbus[['trip_id', 'route_id']], on='trip_id', how='left')
    stt_dbus = stt_dbus.merge(st_dbus[['stop_id', 'stop_name']], on='stop_id', how='left')
    
    # Crear secuencia de paradas
    stt_dbus['stop_sequence'] = stt_dbus.groupby('trip_id').cumcount() + 1
    
    # Crear df_final con velocidades promedio entre paradas
    df_final = stt_dbus.groupby(['route_id', 'stop_id', 'stop_name', 'stop_sequence']).agg(
        avg_speed=('speed_kmh', 'mean')
    ).reset_index().sort_values(['route_id', 'stop_sequence'])
    
    # Añadir información de la siguiente parada
    df_final['next_stop_id'] = df_final.groupby('route_id')['stop_id'].shift(-1)
    df_final['next_stop_name'] = df_final.groupby('route_id')['stop_name'].shift(-1)
    df_final['next_stop_speed'] = df_final.groupby('route_id')['avg_speed'].shift(-1)
    
    # Eliminar la última parada de cada ruta (no tiene siguiente parada)
    df_final = df_final.dropna(subset=['next_stop_id'])
    
    return agency_dbus, calendar_dbus, routes_dbus, stt_dbus, st_dbus, tri_dbus, sha_dbus, df_final

# Cargar datos
agency_dbus, calendar_dbus, routes_dbus, stt_dbus, st_dbus, tri_dbus, sha_dbus, df_final = load_data()

# =============================================
# SELECCIÓN DE RUTA Y PARADAS
# =============================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align: center;">🔍 1. Route and stop selection</h4>', unsafe_allow_html=True)

# Selección de ruta
route_ids = df_final["route_id"].unique()
selected_route = st.selectbox("Select a route:", sorted(route_ids), key="route_selector")

# Filtrar paradas para la ruta seleccionada
route_stops = df_final[df_final["route_id"] == selected_route]

if len(route_stops) < 2:
    st.markdown("""
    <div class="warning-box">
        <h4>⚠️ Warning</h4>
        <p>This route does not have enough stops to analyze.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Crear diccionario de paradas para selección
    stops_options = {f"{row['stop_id']} - {row['stop_name']}": row['stop_id'] 
                    for _, row in route_stops.iterrows()}
    
    # Selección de paradas
    col1, col2 = st.columns(2)
    with col1:
        start_stop = st.selectbox(
            "Starting Station:",
            options=list(stops_options.keys()),
            key="start_stop"
        )
        start_stop_id = stops_options[start_stop]
    
    with col2:
        # Filtrar paradas de destino (deben estar después del origen)
        start_idx = list(stops_options.keys()).index(start_stop)
        valid_end_stops = list(stops_options.keys())[start_idx+1:] if start_idx+1 < len(stops_options) else []
        
        if valid_end_stops:
            end_stop = st.selectbox(
                "Destination:",
                options=valid_end_stops,
                key="end_stop"
            )
            end_stop_id = stops_options[end_stop]
        else:
            st.markdown("""
            <div class="warning-box">
                <h4>⚠️ Advertencia</h4>
                <p>No hay paradas posteriores disponibles para seleccionar como destino.</p>
            </div>
            """, unsafe_allow_html=True)
            end_stop_id = None
    
    if end_stop_id:
        # Calcular velocidad media entre las paradas seleccionadas
        selected_stops = route_stops[
            (route_stops['stop_id'] >= start_stop_id) & 
            (route_stops['stop_id'] <= end_stop_id)
        ]
        
        # Calcular velocidad media ponderada
        avg_speed = selected_stops['avg_speed'].mean()
        num_segments = len(selected_stops)
        
        # Mostrar resultados
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown('<h4 style="text-align: center;">📊 2. Analysis results</h4>', unsafe_allow_html=True)
        st.markdown("""<div style='height: 50px;'></div>""", unsafe_allow_html=True)
        
        # Verificar si hay datos disponibles
        if pd.isna(avg_speed) or num_segments == 0:
            st.markdown("""
            <div class="warning-box">
                <h4>⚠️ Data not available</h4>
                <p>There is no speed information for this combination of stops.</p>
                <p>Possible reasons:</p>
                <ul>
                    <li>No registered trips between these stops</li>
                    <li>Time/distance data is incomplete</li>
                    <li>Selected stops are not consecutive in any trip</li>
                </ul>
                <p>Please try another combination of stops.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🚌 Average Speed", f"{avg_speed:.1f} km/h")
            with col2:
                st.metric("📍 Segments Analyzed", num_segments)
            with col3:
                origin_name = start_stop.split(" - ")[1]
                dest_name = end_stop.split(" - ")[1]
                st.metric("🔢 Stops", f"{origin_name} → {dest_name}")
            
            # --- Comparación con Bicicleta ---
            BIKE_SPEED = 15  # Velocidad media bicicleta
            
            # Determinar qué medio es más rápido
            if avg_speed > BIKE_SPEED:
                st.markdown(f"""
                <div class="bus-recommendation">
                    <h4>✅ Bus Recommended</h4>
                    <p>For this segment, the bus ({avg_speed:.1f} km/h) is faster than the bicycle (15 km/h).</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="bike-recommendation">
                    <h4>🚴 Bicycle Recommendation!</h4>
                    <p>For this segment, the bicycle (15 km/h) would be faster than the bus ({avg_speed:.1f} km/h).</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Gráfico comparativo
                fig = px.bar(
                    x=["Bus", "Bicycle"],
                    y=[avg_speed, BIKE_SPEED],
                    labels={'x': '', 'y': 'Speed (km/h)'},
                    title="Speed comparison",
                    color=["Bus", "Bicycle"],  # Esto asigna categorías para el mapeo de color
                    color_discrete_map={
                        "Bus": "#3498db",     # Azul para el autobús
                        "Bicycle": "#2ecc71"  # Verde para la bicicleta
                    },
                    text=[f"{avg_speed:.1f} km/h", f"{BIKE_SPEED} km/h"]
                )
                fig.update_layout(
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                fig.update_traces(textposition='outside')
                st.plotly_chart(fig, use_container_width=True, key="speed_comparison")
                
                # Estimación de tiempos (solo se muestra cuando la bicicleta es más rápida)
                estimated_distance = num_segments * 0.5  # 0.5 km por tramo (estimado)
                bus_time = (estimated_distance / avg_speed) * 60
                bike_time = (estimated_distance / BIKE_SPEED) * 60
                time_diff = bus_time - bike_time
                
                st.markdown(f"""
                <div style="background:#f8f9fa; border-radius:10px; padding:15px; margin-top:20px;">
                    <h4 style="color:#2c3e50; margin-top:0; text-align: center">Estimated time</h4>
                    <div style="display:flex; justify-content:space-around; margin:15px 0">
                        <div style="text-align:center">
                            <p style="font-weight:bold">🚌 Bus</p>
                            <p style="font-size:24px; color:#3498db">{bus_time:.1f} min</p>
                        </div>
                        <div style="text-align:center">
                            <p style="font-weight:bold">🚲 Bycicle</p>
                            <p style="font-size:24px; color:#2ecc71">{bike_time:.1f} min</p>
                        </div>
                    </div>
                    <p style="text-align:center">
                        The bycicle is <span style="color:#2ecc71; font-weight:bold">{abs(time_diff):.1f} minutes faster</span>
                    </p>
                </div>
                """, unsafe_allow_html=True)

# =============================================
# CONSEJOS ADICIONALES
# =============================================
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.markdown('<h4 style="text-align: center;">💡 3. Tips for Urban Cyclists</h4>', unsafe_allow_html=True)

st.markdown("""
<div class="highlight-box">
    <ul>
        <li>For short distances (&lt;3 km), bikes are usually the fastest option</li>
        <li>Consider weather and your physical condition when choosing transport</li>
        <li>Electric bikes can maintain speeds of 20–25 km/h</li>
        <li>During rush hours, buses may be slower due to traffic</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Cerrar contenedor principal
st.markdown('</div>', unsafe_allow_html=True)