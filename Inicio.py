import streamlit as st

st.set_page_config(
    page_title="Inicio - Dashboard de Crímenes",
    page_icon="👋",
    layout="wide"
)

st.title("👋 Análisis Interactivo de la Criminalidad en Chicago")
st.markdown("Te damos la bienvenida a una herramienta de exploración de los datos de seguridad pública de la ciudad de Chicago.")

st.markdown("---")

st.header("Nuestro Conjunto de Datos")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    La información utilizada en este dashboard proviene del portal de datos abiertos de la Ciudad de Chicago y refleja los incidentes criminales reportados al Departamento de Policía de Chicago (CPD).
    
    - **Fuente Principal:** Sistema CLEAR del Departamento de Policía de Chicago.
    - **Periodo de Análisis:** Se ha acotado el análisis a los datos comprendidos entre los años **2012 y 2016**.
    - **Nivel de Detalle:** Para proteger la privacidad de las víctimas, las ubicaciones se muestran a nivel de cuadra, no en direcciones exactas.
    """)

with col2:
    st.warning("""
    **⚠️ Descargo de Responsabilidad**
    
    Los datos son preliminares y no siempre están verificados. Las clasificaciones pueden cambiar. No se garantiza la precisión y los datos no deben usarse para comparaciones directas a lo largo del tiempo.
    """)

st.markdown("---")

st.header("Explora Nuestras Herramientas de Análisis")
st.markdown("Este dashboard se divide en dos paneles de análisis principales, cada uno con un propósito diferente:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background-color: #262730; border: 1px solid #333; border-radius: 10px; padding: 20px; height: 300px;">
        <h3>🗺️ Mapa de Puntos Calientes</h3>
        <p>Esta herramienta te permite visualizar la distribución geográfica de los crímenes en Chicago.</p>
        <strong>Su finalidad es responder a la pregunta:</strong>
        <p style="font-style: italic; font-size: 1.1em; color: #1f77b4;">"¿Dónde ocurren los delitos?"</p>
        <p>Selecciona uno de los barrios con mayor actividad en la barra lateral para enfocar el mapa, resaltar el área y explorar los crímenes específicos de esa zona.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #262730; border: 1px solid #333; border-radius: 10px; padding: 20px; height: 300px;">
        <h3>🔎 Panel de Métricas y Tendencias</h3>
        <p>Aquí puedes profundizar en las estadísticas detalladas detrás de los datos.</p>
        <strong>Su finalidad es responder a las preguntas:</strong>
        <p style="font-style: italic; font-size: 1.1em; color: #E45756;">"¿Qué delitos predominan y cómo se comportan a lo largo del tiempo?"</p>
        <p>Filtra por tipo de delito para ver sus métricas clave o selecciona un barrio para analizar su perfil de criminalidad y tendencias históricas.</p>
    </div>
    """, unsafe_allow_html=True)