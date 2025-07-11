#python -m streamlit run Traffic_Networks.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os
import folium
from streamlit_folium import st_folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import calendar
import plotly.graph_objects as go

# =============================================
# CONFIGURACIÓN INICIAL (ESTILO COMO PAGINA PRINCIPAL)
# =============================================
st.set_page_config(
    page_title="Traffic Networks", 
    page_icon="🚦", 
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
# BOTONES DE NAVEGACIÓN
# =============================================

st.markdown('<h1 class="main-title">🚲Traffic Networks</h1>', unsafe_allow_html=True)

# Botón de retorno centrado
col_centered = st.columns([1, 1, 1])  # Columnas para centrar el botón
with col_centered[1]:
    if st.button("🏠 Return to Main Menu", key="btn_main_menu"):
        st.session_state.page_to_load = "Pagina_Principal.py"
        st.switch_page("Pagina_Principal.py")

# Tres columnas con botones y descripciones
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Statistical Measures", key="btn_modelizacion"):
        st.session_state.show_section = "modelizacion"
    st.markdown("""
    <div style="margin-top: 15px; text-align: center;">
        Analyze traffic patterns and statistical distributions across different stations and time periods.
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("📅 Temporal Analysis", key="btn_analisis"):
        st.session_state.show_section = "analisis"
    st.markdown("""
    <div style="margin-top: 15px; text-align: center;">
        Examine how traffic flows change over time, including daily, weekly, and seasonal variations.
    </div>
    """, unsafe_allow_html=True)

with col3:
    if st.button("🗺️ Stations Map", key="mapa"):
        st.session_state.show_section = "mapa"
    st.markdown("""
    <div style="margin-top: 15px; text-align: center;">
        Interactive map showing traffic station locations and spatial distribution patterns.
    </div>
    """, unsafe_allow_html=True)

# Inicializar sección si no existe
if "show_section" not in st.session_state:
    st.session_state.show_section = "all"

# =============================================
# CARGA DE DATOS
# =============================================
carpeta = "Datos 2"
lista_df = []
columnas_requeridas = ['Fecha', 'Hora']

for i, Datos in enumerate(os.listdir(carpeta)):
    base_datos = os.path.join(carpeta, Datos)
    
    if Datos.lower() == 'estaciones.csv':
        try:
            df_estaciones = pd.read_csv(base_datos, delimiter=";", encoding='latin1')
            st.session_state.datos_estaciones = df_estaciones
            continue
        except Exception as e:
            continue
    
    if base_datos.endswith('.csv'):
        try:
            try:
                df = pd.read_csv(base_datos, delimiter=";", encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(base_datos, delimiter=";", encoding='latin1')
            
            if not all(col in df.columns for col in columnas_requeridas):
                st.warning(f"File {Datos} skipped - missing columns")
                continue
                
            if i > 0:
                df = df.iloc[1:].reset_index(drop=True)
            
            df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)
            df['Hora'] = df['Hora'].astype(str)
            
            for col in df.columns:
                if 'ligeros' in col or 'pesados' in col:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            lista_df.append(df)
            
        except Exception as e:
            st.error(f"Error processing {Datos}: {str(e)}")
            continue

# Combinar todos los DataFrames válidos
if lista_df:
    df_final = pd.concat(lista_df, ignore_index=True)
    
    # Limpieza final
    df_final = df_final.dropna(subset=columnas_requeridas)
    df_final['DiaSemana'] = df_final['Fecha'].dt.day_name()
    df_final['Mes'] = df_final['Fecha'].dt.month
    
    # Identificar automáticamente columnas de carriles
    columnas_carriles = [col for col in df_final.columns if 'ligeros' in col.lower() or 'pesados' in col.lower()]
    df_final['Total_Vehiculos'] = df_final[columnas_carriles].sum(axis=1)

    # 🔁 AÑADIR AQUÍ:
    df_final['Day_Type'] = df_final['Fecha'].dt.dayofweek.apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
# ============================================================================================================================================
# SECCIÓN 1: Statical Modeling
# ============================================================================================================================================
if st.session_state.show_section in ["all", "modelizacion"]:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title"><strong>Statistical Measures<strong></h2>', unsafe_allow_html=True)
    
    # ----------------------------
    # 1. Resumen Estadístico Básico
    # ----------------------------
    with st.expander("📊 Basic Statistical Summary", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        # Estadísticos clave
        total_vehicles = df_final['Total_Vehiculos'].sum()
        avg_per_station = df_final.groupby('Estacion')['Total_Vehiculos'].mean().mean()
        peak_hour = df_final.groupby('Hora')['Total_Vehiculos'].mean().idxmax()
        
        col1.metric("Total Vehicles Recorded", f"{total_vehicles:,}")
        col2.metric("Avg Vehicles per Station", f"{avg_per_station:,.0f}")
        col3.metric("Peak Traffic Hour", f"{peak_hour}:00")


  
    # Boxplot por estación
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<h4 style="text-align: center;">🚦 1. Traffic Distribution by Station</h4>', unsafe_allow_html=True)
        
        if 'Estacion' in df_final.columns and 'Total_Vehiculos' in df_final.columns:
            top_estaciones = df_final.groupby('Estacion')['Total_Vehiculos'].median().nlargest(5).index
            estaciones_seleccionadas = st.multiselect("Select stations:", df_final['Estacion'].unique(), default=list(top_estaciones), key="estaciones_boxplot")
            
            if estaciones_seleccionadas:
                estacion_a_numero = {estacion: i+1 for i, estacion in enumerate(estaciones_seleccionadas)}
                df_boxplot = df_final[df_final['Estacion'].isin(estaciones_seleccionadas)].copy()
                df_boxplot['Estacion_Numero'] = df_boxplot['Estacion'].map(estacion_a_numero)
                
                fig = px.box(
                    df_boxplot,
                    x='Estacion_Numero', 
                    y='Total_Vehiculos',
                    color='Estacion',
                    title="Traffic distribution by station",
                    labels={'Estacion_Numero': 'Station'}
                )
                
                fig.update_xaxes(
                    tickvals=list(estacion_a_numero.values()),
                    ticktext=[f"Station {num}" for num in estacion_a_numero.values()]
                )
                
                st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Evolución horaria
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<h4 style="text-align: center;">🕒 2. Traffic Evolution by Hour (Multi-Year Comparison)</h4>', unsafe_allow_html=True)
        
        años_seleccionados = st.multiselect(
            "Select year(s):", 
            df_final['Fecha'].dt.year.unique(),
            default=[df_final['Fecha'].dt.year.unique()[-1]],
            key="year_multiselect"
        )
        
        estaciones_evolucion = st.multiselect(
            "Select stations to display:", 
            df_final['Estacion'].unique(),
            default=df_final['Estacion'].unique()[:3],
            key="estaciones_evolucion"
        )
        
        df_filtrado = df_final[
            (df_final['Fecha'].dt.year.isin(años_seleccionados)) & 
            (df_final['Estacion'].isin(estaciones_evolucion))
        ]
        
        if not df_filtrado.empty and len(años_seleccionados) > 0:
            df_filtrado['Año-Estación'] = df_filtrado['Fecha'].dt.year.astype(str) + " - " + df_filtrado['Estacion'].astype(str)
            
            fig = px.line(
                df_filtrado.groupby(['Hora', 'Año-Estación', 'Estacion', df_filtrado['Fecha'].dt.year])['Total_Vehiculos'].mean().reset_index(),
                x='Hora', 
                y='Total_Vehiculos',
                color='Año-Estación',
                title=f"Hourly evolution comparison",
                labels={'Año-Estación': 'Year - Station'},
                line_dash='Estacion',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            
            fig.update_layout(
                legend_title_text='Year & Station',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select at least one year and one station.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================================================================================================================================
# SECCIÓN 2: Temporal Analysis (Versión Mejorada)
# ==========================================================================================================================================================
if st.session_state.show_section in ["all", "analisis"]:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title"><strong>Temporal Analysis<strong></h2>', unsafe_allow_html=True)
    
    # ----------------------------
    # 1. TRÁFICO SEMANAL POR CARRETERA (Modificado)
    # ----------------------------
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<h4 style="text-align: center;">📅 1. Weekly Traffic Pattern by Road</h4>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_road = st.selectbox(
                "Select road:",
                df_final['Estacion'].unique(),
                key="weekly_road"
            )
        with col2:
            selected_year = st.selectbox(
                "Select year:",
                sorted(df_final['Fecha'].dt.year.unique()),
                index=len(df_final['Fecha'].dt.year.unique())-1,
                key="weekly_year"
            )
        with col3:
            selected_month = st.selectbox(
                "Select month:",
                range(1,13),
                format_func=lambda x: calendar.month_name[x],
                key="weekly_month"
            )
        
        # Filtrar y procesar datos
        df_filtered = df_final[
            (df_final['Estacion'] == selected_road) &
            (df_final['Fecha'].dt.year == selected_year) &
            (df_final['Fecha'].dt.month == selected_month)
        ].copy()
        
        if not df_filtered.empty:
            df_filtered['DiaSemana'] = df_filtered['Fecha'].dt.day_name()
            df_filtered['DiaSemana'] = pd.Categorical(df_filtered['DiaSemana'], 
                                                     categories=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
                                                     ordered=True)
            
            weekly_avg = df_filtered.groupby('DiaSemana')['Total_Vehiculos'].mean().reset_index()
            
            # Gráfico de área mejorado
            fig = px.area(
                weekly_avg,
                x='DiaSemana',
                y='Total_Vehiculos',
                title=f"Weekly Traffic on {selected_road} ({calendar.month_name[selected_month]} {selected_year})",
                labels={'Total_Vehiculos': 'Average Vehicles'},
                line_shape='linear',  # Línea recta
                color_discrete_sequence=['#3498db']
            )
            
            # Personalización adicional
            fig.update_traces(
                fill='tozeroy',  # Relleno hasta el eje y=0
                line=dict(width=3),
                mode='lines+markers'
            )
            
            fig.update_layout(
                xaxis_title='',
                yaxis_title="Average Vehicles",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for selected filters")

    # ----------------------------
    # 2. DISTRIBUCIÓN MENSUAL (Manteniendo)
    # ----------------------------
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<h4 style="text-align: center;">📊 2. Monthly Distribution by Road</h4>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            road_monthly = st.selectbox(
                "Select road:",
                df_final['Estacion'].unique(),
                key="monthly_road"
            )
        with col2:
            year_monthly = st.selectbox(
                "Select year:",
                sorted(df_final['Fecha'].dt.year.unique()),
                index=len(df_final['Fecha'].dt.year.unique())-1,
                key="monthly_year"
            )
        
        df_monthly = df_final[
            (df_final['Estacion'] == road_monthly) &
            (df_final['Fecha'].dt.year == year_monthly)
        ]
        
        monthly_avg = df_monthly.groupby('Mes')['Total_Vehiculos'].mean().reset_index()
        monthly_avg['Month_Name'] = monthly_avg['Mes'].apply(lambda x: calendar.month_name[x])
        
        fig = px.bar(
            monthly_avg,
            x='Month_Name',
            y='Total_Vehiculos',
            title=f"Monthly Traffic on {road_monthly} ({year_monthly})",
            labels={'Total_Vehiculos': 'Average Vehicles'},
            color='Total_Vehiculos',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(xaxis_title="", coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------
    # 3. EVOLUCIÓN ANUAL (Estilo Alternativo)
    # ----------------------------
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<h4 style="text-align: center;">📊 3. Yearly Traffic Evolution</h4>', unsafe_allow_html=True)

        # Controles en una sola fila
        cols = st.columns([3, 1, 1])
        with cols[0]:
            road_yearly = st.selectbox(
                "Select road:",
                df_final['Estacion'].unique(),
                key="yearly_road"
            )

        with cols[1]:
            show_ci = st.checkbox("Show CI", value=True, key="ci_checkbox")

        with cols[2]:
            show_trend = st.checkbox("Show trend", value=True, key="trend_checkbox")

        # Preparar datos
        df_yearly = df_final[df_final['Estacion'] == road_yearly]
        yearly_stats = df_yearly.groupby(df_yearly['Fecha'].dt.year)['Total_Vehiculos'].agg(['mean','std','count']).reset_index()
        yearly_stats.columns = ['Year', 'Average', 'Std', 'Count']

        # Crear gráfico con estilo minimalista
        fig = go.Figure()

        # Línea principal con marcadores
        fig.add_trace(go.Scatter(
            x=yearly_stats['Year'],
            y=yearly_stats['Average'],
            mode='lines+markers',
            line=dict(color='#4C78A8', width=3),
            marker=dict(size=8, color='#4C78A8', line=dict(width=1, color='DarkSlateGrey')),
            name='Average Traffic',
            hovertemplate='Year: %{x}<br>Vehicles: %{y:,.0f}<extra></extra>'
        ))

        # Intervalo de confianza (opcional)
        if show_ci:
            yearly_stats['CI_lower'] = yearly_stats['Average'] - 1.96*(yearly_stats['Std']/np.sqrt(yearly_stats['Count']))
            yearly_stats['CI_upper'] = yearly_stats['Average'] + 1.96*(yearly_stats['Std']/np.sqrt(yearly_stats['Count']))

            fig.add_trace(go.Scatter(
                x=yearly_stats['Year'],
                y=yearly_stats['CI_upper'],
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))

            fig.add_trace(go.Scatter(
                x=yearly_stats['Year'],
                y=yearly_stats['CI_lower'],
                fill='tonexty',
                mode='lines',
                line=dict(width=0),
                fillcolor='rgba(76, 120, 168, 0.2)',
                name='95% CI',
                hoverinfo='skip'
            ))

        # Línea de tendencia (opcional)
        if show_trend and len(yearly_stats) > 2:
            z = np.polyfit(yearly_stats['Year'], yearly_stats['Average'], 1)
            p = np.poly1d(z)

            fig.add_trace(go.Scatter(
                x=yearly_stats['Year'],
                y=p(yearly_stats['Year']),
                mode='lines',
                line=dict(color='#E45756', width=2, dash='dot'),
                name='Trend Line'
            ))

        # Personalización avanzada
        fig.update_layout(
            title=f"<b>Annual Traffic Evolution</b><br><sup>{road_yearly}</sup>",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridcolor='lightgrey',
                title='Year',
                tickmode='linear'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='lightgrey',
                title='Average Vehicles',
                rangemode='tozero'
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=20, r=20, t=80, b=20)
        )
    
    st.plotly_chart(fig, use_container_width=True)
    # ----------------------------
    # 4. SEASONAL TRENDS (Manteniendo tu versión original)
    # ----------------------------
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<h4 style="text-align: center;">🌸 4. Seasonal Traffic Trends</h4>', unsafe_allow_html=True)

        # Función para estaciones climáticas
        def get_season(date):
            month = date.month
            if month in [12, 1, 2]: return 'Winter'
            elif month in [3, 4, 5]: return 'Spring'
            elif month in [6, 7, 8]: return 'Summer'
            else: return 'Autumn'

        # Selector de año
        selected_year = st.selectbox(
            "Select year:",
            sorted(df_final['Fecha'].dt.year.unique()),
            index=len(df_final['Fecha'].dt.year.unique())-1,
            key="seasonal_year"
        )

        # Procesamiento de datos
        df_season = df_final[df_final['Fecha'].dt.year == selected_year].copy()
        df_season['Season'] = df_season['Fecha'].apply(get_season)

        season_avg = df_season.groupby('Season')['Total_Vehiculos'].mean().reset_index()
        season_order = ['Winter', 'Spring', 'Summer', 'Autumn']
        season_avg['Season'] = pd.Categorical(season_avg['Season'], categories=season_order, ordered=True)
        season_avg = season_avg.sort_values('Season')

        # Gráfico de barras mejorado
        fig = px.bar(
            season_avg,
            x='Season',
            y='Total_Vehiculos',
            title=f'Seasonal Traffic Patterns ({selected_year})',
            labels={'Total_Vehiculos': 'Average Vehicles'},
            color='Season',
            color_discrete_sequence=['#FF7F0E', '#2CA02C', '#1F77B4', '#D62728']  # Colores distintivos
        )
        
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ==================================================================================================================================
# SECCIÓN 3: MAPA DE ESTACIONES DE TRÁFICO
# ==================================================================================================================================
if st.session_state.show_section in ["all", "mapa"]:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title"><strong>Stations Map</strong></h2>', unsafe_allow_html=True)
    
    # Load station data
    carpeta = "Datos 2"
    estaciones_file = os.path.join(carpeta, "estaciones.csv")
    
    try:
        df_estaciones = pd.read_csv(estaciones_file, encoding='latin1', delimiter=';', index_col=False)
        st.session_state.datos_estaciones = df_estaciones
    except Exception as e:
        st.error(f"Error loading stations file: {str(e)}")
        df_estaciones = pd.DataFrame()

    # Map section - ahora ocupa todo el ancho
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<h4 style="text-align: center;">🗺️ 1. Traffic Stations Map</h4>', unsafe_allow_html=True)
    
    if not df_estaciones.empty and 'X' in df_estaciones.columns and 'Y' in df_estaciones.columns:
        # Create station selection dropdown - ahora es el primer selector
        station_list = df_estaciones['ETD code'].unique().tolist()
        selected_station = st.selectbox(
            "Select a station to zoom to:",
            options=["All Stations"] + station_list,
            index=0
        )
        
        # Create map centered on average or selected station
        centro_mapa = [df_estaciones['Y'].mean(), df_estaciones['X'].mean()]
        zoom_start = 11
        
        # If a specific station is selected, center the map on it
        if selected_station != "All Stations":
            station_data = df_estaciones[df_estaciones['ETD code'] == selected_station].iloc[0]
            centro_mapa = [station_data['Y'], station_data['X']]
            zoom_start = 13
        
        mapa = folium.Map(location=centro_mapa, zoom_start=zoom_start, width='100%')
        
        # Add markers for each station
        for idx, row in df_estaciones.iterrows():
            is_selected = (selected_station != "All Stations" and row['ETD code'] == selected_station)
            
            folium.Marker(
                location=[row['Y'], row['X']],
                popup=f"ETD code: {row['ETD code']}<br>X: {row['X']}<br>Y: {row['Y']}",
                icon=folium.Icon(
                    color='red' if is_selected else 'blue', 
                    icon='info-sign'
                )
            ).add_to(mapa)
            
            # Add circle to highlight selected station
            if is_selected:
                folium.Circle(
                    location=[row['Y'], row['X']],
                    radius=100,
                    color='red',
                    fill=True,
                    fill_color='red',
                    fill_opacity=0.2
                ).add_to(mapa)
        
        # Display the map
        st_folium(mapa, use_container_width=True, height=800)
    else:
        st.warning("No valid station data available for the map", icon="⚠️")

    # Divider between map and chart
    st.markdown('<hr style="margin: 30px 0;">', unsafe_allow_html=True)

    # Traffic pattern analysis section
    st.markdown('<h4 style="text-align: center;">🕒 2. Traffic Patterns Analysis</h4>', unsafe_allow_html=True)

    if not df_final.empty:
        selected_road = selected_station if 'selected_station' in locals() and selected_station != "All Stations" else df_final['Estacion'].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            selected_month = st.selectbox(
                "Month:",
                options=['All Months'] + list(range(1, 13)),
                format_func=lambda x: calendar.month_name[x] if x != 'All Months' else 'All Months'
            )
        with col2:
            analysis_mode = st.radio(
                "View mode:",
                options=['Hourly', 'Daily'],
                horizontal=True
            )

        df_filtered = df_final[df_final['Estacion'] == selected_road]
        if selected_month != 'All Months':
            df_filtered = df_filtered[df_filtered['Fecha'].dt.month == selected_month]
        
        if not df_filtered.empty:
            df_filtered = df_filtered.copy()
            df_filtered['Hora'] = df_filtered['Hora'].astype(str).str.split(':').str[0].astype(int)
            
            traffic_levels = df_filtered['Total_Vehiculos'].quantile([0.25, 0.75]).values
            low_traffic = traffic_levels[0]
            high_traffic = traffic_levels[1]

            if analysis_mode == 'Hourly':
                day_type = st.radio(
                    "Traffic type:",
                    options=['Weekdays', 'Weekends', 'Compare'],
                    horizontal=True
                )
                
                if day_type == 'Weekdays':
                    plot_data = df_filtered[df_filtered['Fecha'].dt.dayofweek < 5]
                    color_scale = ['#3A86FF']
                elif day_type == 'Weekends':
                    plot_data = df_filtered[df_filtered['Fecha'].dt.dayofweek >= 5]
                    color_scale = ['#FF6B6B']
                else:
                    plot_data = df_filtered
                    color_scale = ['#3A86FF', '#FF6B6B']
                
                agg_data = plot_data.groupby(['Hora', 'Day_Type'] if day_type == 'Compare' else ['Hora'])['Total_Vehiculos'].mean().reset_index()
                
                fig = px.bar(
                    agg_data,
                    x='Hora',
                    y='Total_Vehiculos',
                    color='Day_Type' if day_type == 'Compare' else None,
                    barmode='group',
                    title=f'Hourly Traffic on {selected_road}',
                    color_discrete_sequence=color_scale
                )
                
                fig.add_hline(y=low_traffic, line_dash="dot", line_color="green", 
                            annotation_text="Low Traffic", annotation_position="bottom right")
                fig.add_hline(y=high_traffic, line_dash="dot", line_color="red", 
                            annotation_text="High Traffic", annotation_position="top right")
                
                fig.update_xaxes(tickvals=list(range(24)), title="Hour of Day")
                
            else:
                plot_data = df_filtered.copy()
                plot_data['Day_Name'] = plot_data['Fecha'].dt.day_name()
                agg_data = plot_data.groupby('Day_Name')['Total_Vehiculos'].mean().reset_index()
                
                fig = px.bar(
                    agg_data,
                    x='Day_Name',
                    y='Total_Vehiculos',
                    title=f'Daily Traffic on {selected_road}',
                    color_discrete_sequence=['#636EFA']
                )
                
                fig.add_hline(y=low_traffic, line_dash="dot", line_color="green", 
                            annotation_text="Low Traffic", annotation_position="bottom right")
                fig.add_hline(y=high_traffic, line_dash="dot", line_color="red", 
                            annotation_text="High Traffic", annotation_position="top right")
                
                fig.update_xaxes(categoryorder='array', 
                                categoryarray=list(calendar.day_name),
                                title="Day of Week")

            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                hovermode="x unified",
                height=500,
                yaxis_title="Average Vehicles"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            <div style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: -15px;">
                <strong>Traffic Guide:</strong><br>
                <span style="color: green;">• Low Traffic</span> (Bottom 25%) | 
                <span style="color: orange;">• Normal Traffic</span> | 
                <span style="color: red;">• High Traffic</span> (Top 25%)
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("No data available for selected filters", icon="⚠️")
    else:
        st.warning("No traffic data available", icon="⚠️")