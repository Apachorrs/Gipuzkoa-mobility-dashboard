#python -m streamlit run Pagina_Principal.py
#pip install -r requirements.txt
import streamlit as st
from datetime import datetime
import streamlit.components.v1 as components

# Controlador de navegación
if 'page_to_load' in st.session_state:
    target = st.session_state.page_to_load
    del st.session_state.page_to_load  # Limpiamos después de usar
    st.switch_page(target)

# Configuración de la página
st.set_page_config(
    page_title="Gipuzkoa Mobility Insights: Data-Driven Transport Solutions", 
    page_icon="🌍", 
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
    
    .subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1.5rem;
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    .options-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 2rem;
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
    }
    
    .option-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
    }
    
    .option-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .option-title {
        font-size: 1.3rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .option-desc {
        color: #7f8c8d;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
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
    
    @media (max-width: 1200px) {
        .options-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .options-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""", unsafe_allow_html=True)

# Función para crear tarjetas con botones que funcionan
def create_option_card(icon, title, description, button_text, page):
    """Crea una tarjeta de opción con un botón funcional"""
    with st.container():
        st.markdown(f"""
        <div class="option-card">
            <div class="option-icon">{icon}</div>
            <div class="option-title">{title}</div>
            <div class="option-desc">{description}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(button_text, key=f"btn_{page}"):
            st.session_state.page = f"pages/{page}"
            st.switch_page(f"pages/{page}")

# Contenido principal
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Título y subtítulo
st.markdown('<h1 class="main-title">Gipuzkoa Mobility Insights: Data-Driven Transport Solutions</h1>', unsafe_allow_html=True)
st.markdown('<h2 class="subtitle">Gipuzkoa Region Mobility Analysis Platform</h2>', unsafe_allow_html=True)

# Crear las opciones
cols = st.columns(4)

with cols[0]:
    create_option_card(
        "🚍", 
        "Bus Routes Analysis", 
        "Analyze bus routes, schedules and trajectories", 
        "Explore", 
        "Bus_Stations.py"
    )

with cols[1]:
    create_option_card(
        "🌍", 
        "Travel Time Heat Map", 
        "Interactive heat map to detect delays and bottlenecks", 
        "View Map", 
        "Interactive_map.py"
    )

with cols[2]:
    create_option_card(
        "🚦", 
        "Traffic Networks", 
        "Analyze urban traffic flow and connectivity patterns across Gipuzkoa", 
        "Analyze", 
        "Traffic_networks.py"
    )

with cols[3]:
    create_option_card(
        "⏱️", 
        "Time Efficiency", 
        "Compare transport modes for optimal travel", 
        "Evaluate", 
        "Time_efficiency.py"
    )

st.markdown('</div>', unsafe_allow_html=True)

# Pie de página con nombres y universidad
st.markdown("""
<hr style="margin-top: 3rem; margin-bottom: 1rem; border: none; border-top: 1px solid #ccc;">

<div style="text-align: center; color: #7f8c8d; font-size: 0.9rem; margin-top: 1.5rem;">
    <p><strong>Developed by:</strong> Juan Pablo Queralt, Samuel Jiménez, Kerman Martin, Roberto Rubio, Jose Francisco Navarro</p>
    <p>Universidad de Navarra - Tecnun ©</p>
</div>
""", unsafe_allow_html=True)
