import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

# Configuración de la página para usar todo el ancho
st.set_page_config(layout="wide")


# Título de la página
st.markdown("<h1 style='text-align: center;'>Traffic Networks 🚦</h1>", unsafe_allow_html=True)

st.markdown("""
<style>
    div.stButton > button {
        display: block;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Botón para regresar al menú principal
if st.button("Return to Main Menu"):
    st.session_state.page = "Pagina_Principal.py"
    st.switch_page("Pagina_Principal.py")

# Introduction
st.markdown(
    """
    <div style="text-align: center;">
        <h3>Introduction</h3>
        <p>The goal of this page is to provide a detailed analysis of the traffic evolution across the different mobility networks in Gipuzkoa, in order to make more informed decisions regarding transportation and mobility organization.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Carpeta donde están los archivos CSV
carpeta = "Datos 2"

# Lista para almacenar los DataFrames
lista_df = []

# Iterar sobre los archivos en la carpeta
for i, Datos in enumerate(os.listdir(carpeta)):
    base_datos = os.path.join(carpeta, Datos)
    
    # Solo leer archivos CSV
    if base_datos.endswith('.csv'):
        try:
            df = pd.read_csv(base_datos, delimiter=";")
            
            # Verificar si las columnas necesarias están presentes
            if 'Fecha' not in df.columns or 'Hora' not in df.columns:
                print(f"Advertencia: El archivo {base_datos} no tiene las columnas 'Fecha' o 'Hora'. Se omitirá este archivo.")
                continue  
            
            # Si no es el primer archivo, eliminar la primera fila
            if i > 0:
                df = df.iloc[1:].reset_index(drop=True)
            
            df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)
            df['Hora'] = df['Hora'].astype(str)
            
            # Convertir columnas de carriles a enteros
            for col in df.columns:
                if 'ligeros' in col or 'pesados' in col:
                    df[col] = df[col].astype(int)
            
            lista_df.append(df)
        except Exception as e:
            print(f"Error al leer el archivo {base_datos}: {e}")

# Concatenar DataFrames
if lista_df:
    df_final = pd.concat(lista_df, ignore_index=True)
    
    # Limpiar los datos NaN: eliminar filas con NaN
    df_final = df_final.dropna()  

    df_final['DiaSemana'] = df_final['Fecha'].dt.day_name()
    df_final['Mes'] = df_final['Fecha'].dt.month

    columnas_carriles = df_final.columns[3:15]
    
    ############################################################# 0. Show data frame
    st.markdown(
    """
    <div style="text-align: center;">
        <h3>0. Data Preview</h3>
    </div>
    """,
    unsafe_allow_html=True
    )
    st.dataframe(df_final.head(50))   

    ############################################################ 1. Media por estación
    st.markdown(
    """
    <div style="text-align: center;">
        <h3>1. Mean By Station</h3>
    </div>
    """,
    unsafe_allow_html=True
    )

    media_por_estacion = df_final.groupby('Estacion')[columnas_carriles].mean()

   # Crear columnas vacías a los lados para centrar el DataFrame
    col1, col2, col3 = st.columns([1, 7, 1])  # Ajusta los valores para cambiar el ancho

    with col2:
        st.dataframe(media_por_estacion.head(50))

    ############################################################# 2. Media por hora
    st.markdown(
    """
    <div style="text-align: center;">
        <h3>2. Mean By Hour</h3>
    </div>
    """,
    unsafe_allow_html=True
    )

    media_por_hora = df_final.groupby("Hora")[columnas_carriles].mean()

    # Crear columnas vacías a los lados para centrar el DataFrame
    col1, col2, col3 = st.columns([1, 7, 1])  # Ajusta los valores para cambiar el ancho

    with col2:
        st.dataframe(media_por_hora)

    ############################################################# 3. Desviación estándar por estación
    st.markdown(
    """
    <div style="text-align: center;">
        <h3>3. Standar Deviation By Station</h3>
    </div>
    """,
    unsafe_allow_html=True
    )

    std_por_estacion = df_final.groupby('Estacion')[columnas_carriles].std()
    
    # Crear columnas vacías a los lados para centrar el DataFrame
    col1, col2, col3 = st.columns([1, 7, 1])  # Ajusta los valores para cambiar el ancho

    with col2:
        st.dataframe(std_por_estacion.head(50))

    ############################################################# 4. Horas punta (horas con mayor tráfico total)

    st.markdown(
    """
    <div style="text-align: center;">
        <h3>4. Peak hours (Hours with the highest total traffic), percentage of heavy vehicles, and monthly trends</h3>
    </div>
    """,
    unsafe_allow_html=True
    )

    df_final['Total_Vehiculos'] = df_final[columnas_carriles].sum(axis=1)
    horas_punta = df_final.groupby("Hora")['Total_Vehiculos'].mean().sort_values(ascending=False)

    columnas_pesados = [col for col in columnas_carriles if 'pesados' in col]
    df_final['Porcentaje_Pesados'] = df_final[columnas_pesados].sum(axis=1) / df_final['Total_Vehiculos'] * 100
    porcentaje_pesados = df_final.groupby("Estacion")["Porcentaje_Pesados"].mean()

    tendencia_mensual = df_final.groupby("Mes")['Total_Vehiculos'].mean()

    # Crear columnas vacías a los lados para centrar el DataFrame
    col1, col2, col3, col4, col5, col6, col7, col8, col9= st.columns([3.8, 3, 1, 1, 3, 1, 1.4, 5, 1])

    with col2:
        st.dataframe(horas_punta)
    with col5:
        st.dataframe(porcentaje_pesados.head(20))  
    with col8:
        st.dataframe(tendencia_mensual)

    ############################################################# 7.Gráfico de histograma de las tendencias mensuales
    st.markdown(
    """
    <div style="text-align: center;">
        <h3>7. Average number of vehicles per month</h3>
    </div>
    """,
    unsafe_allow_html=True
    )
    df_tendencia_mensual = pd.DataFrame({
        'Mes': tendencia_mensual.index,
        'Promedio de vehículos': tendencia_mensual.values
    })

    fig = px.bar(df_tendencia_mensual, x='Mes', y='Promedio de vehículos',
                labels={'Mes': 'Month (Number)', 'Promedio de vehículos': 'Vehicles average'})

    st.plotly_chart(fig)
    
    ############################################################# 8. Boxplot Mejorado: Tráfico por Estación
    st.markdown(
        """
        <div style="text-align: center;">
            <h3>8. Boxplot: Ordered Traffic by Station</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Verificar que las columnas necesarias existen en df_final
    if 'Estacion' in df_final.columns and 'Total_Vehiculos' in df_final.columns:
        df_final['Total_Vehiculos'] = pd.to_numeric(df_final['Total_Vehiculos'], errors='coerce')

        # Calcular la mediana del tráfico por estación para ordenar
        trafico_median = df_final.groupby('Estacion')['Total_Vehiculos'].median().sort_values(ascending=False)

        # Tomar las 10 estaciones con mayor mediana de tráfico
        top_estaciones = trafico_median.head(10).index.tolist()

        # Selección de estaciones con opción de cambiar
        estaciones_seleccionadas = st.multiselect("Select Stations", trafico_median.index, default=top_estaciones)

        # Filtrar el DataFrame según las estaciones seleccionadas
        df_filtrado = df_final[df_final['Estacion'].isin(estaciones_seleccionadas)]

        if not df_filtrado.empty:
            # Crear boxplot con Plotly
            fig = px.box(df_filtrado, x='Estacion', y='Total_Vehiculos', 
                         labels={"Estacion": "Station", "Total_Vehiculos": "Total Vehicles"},
                         color='Estacion')

            fig.update_layout(
                xaxis_title_font_size=22,  # Tamaño de la fuente del título del eje X
                yaxis_title_font_size=20,  # Tamaño de la fuente del título del eje Y
                title='',
                title_x=0.5,
                legend_font_size=16,  # Tamaño de la fuente de la leyenda
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected stations. Try selecting different stations.")
    else:
        st.error("The necessary columns are missing in the dataset.")

    ############################################################# 9. Filtros interactivos en Streamlit
    años_disponibles = df_final['Fecha'].dt.year.unique()
    año_seleccionado = st.selectbox("Select Year", años_disponibles, index=0)

    # Filtrar datos por el año seleccionado
    df_filtrado = df_final[df_final['Fecha'].dt.year == año_seleccionado]

    # Seleccionar estaciones
    estaciones_disponibles = df_filtrado["Estacion"].unique()
    estaciones_predefinidas = list(estaciones_disponibles[:3]) if len(estaciones_disponibles) >= 3 else list(estaciones_disponibles)
    estaciones_seleccionadas = st.multiselect("Select Stations", estaciones_disponibles, default=estaciones_predefinidas)

    # Filtrar datos por estaciones seleccionadas
    df_filtrado = df_filtrado[df_filtrado["Estacion"].isin(estaciones_seleccionadas)]

    # Agrupar por hora y estación para obtener la media de vehículos en cada hora
    df_agrupado = df_filtrado.groupby(["Hora", "Estacion"])["Total_Vehiculos"].mean().reset_index()

    # Crear gráfico de líneas con puntos
    fig = px.line(df_agrupado, x="Hora", y="Total_Vehiculos", 
                  color="Estacion" if len(estaciones_seleccionadas) > 1 else None,  # Color solo si hay varias estaciones
                  markers=True,  # Mostrar puntos en la línea
                  title=f"Traffic Evolution ({año_seleccionado})",
                  labels={"Hora": "Hour", "Total_Vehiculos": "Total Vehicles"},
                  hover_data=["Estacion"])

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)



#ANALISIS

#1 Analisis temporal

# Análisis por día de la semana y por año
st.markdown(
    """
    <div style="text-align: center;">
        <h3>Tráfico por Día de la Semana (por Año)</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# Asegurarse de que la columna 'Fecha' y 'Total_Vehiculos' existen
if 'Fecha' in df_final.columns and 'Total_Vehiculos' in df_final.columns:
    # Crear una nueva columna con el nombre del día de la semana (Lunes, Martes, etc.)
    df_final['DiaSemana'] = df_final['Fecha'].dt.day_name()

    # Filtrar por año seleccionado
    año_seleccionado = st.selectbox("Selecciona el Año", df_final['Fecha'].dt.year.unique(), index=0)
    
    # Filtrar los datos por el año seleccionado
    df_filtrado = df_final[df_final['Fecha'].dt.year == año_seleccionado]
    
    # Agrupar por día de la semana y calcular el tráfico promedio
    df_agrupado_dia = df_filtrado.groupby(['DiaSemana'])['Total_Vehiculos'].mean().reset_index()

    # Reordenar los días de la semana para que aparezcan de forma lógica (lunes, martes, ...)
    dias_orden = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_agrupado_dia['DiaSemana'] = pd.Categorical(df_agrupado_dia['DiaSemana'], categories=dias_orden, ordered=True)
    df_agrupado_dia = df_agrupado_dia.sort_values('DiaSemana')

    # Mostrar el dataframe con el tráfico promedio por día de la semana
    st.dataframe(df_agrupado_dia)
    
    # Crear gráfico de barras para visualizar el tráfico promedio por día de la semana
    fig = px.bar(df_agrupado_dia, x='DiaSemana', y='Total_Vehiculos',
                 labels={'DiaSemana': 'Día de la Semana', 'Total_Vehiculos': 'Promedio de Vehículos'},
                 title=f"Tráfico Promedio por Día de la Semana ({año_seleccionado})")
    
    # Mostrar gráfico en Streamlit
    st.plotly_chart(fig)