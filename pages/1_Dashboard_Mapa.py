import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import altair as alt
import plotly.graph_objects as go


st.set_page_config(
    page_title="Dashboard de Crímenes en Chicago",
    page_icon="🚨",
    layout="wide"
)

@st.cache_data
def load_data():
    """Carga, preprocesa y calcula los hotspots."""
    gdf_bounds = gpd.read_file('chicago_bounds.geojson')
    df = pd.read_parquet('data/crimes_cleaned.parquet')
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df = df[df['Year'] != 2017] ### Eliminacion del año 2017
    
    df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True, errors='ignore')
    df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True, errors='ignore')

    df.dropna(subset=['lat', 'lon'], inplace=True)
    
    gdf_crimes = gpd.GeoDataFrame(
        df, 
        geometry=gpd.points_from_xy(df.lon, df.lat), 
        crs=gdf_bounds.crs
    )
    
    gdf_crimes_with_areas = gpd.sjoin(gdf_crimes, gdf_bounds, how="inner", predicate='within') ## Join para el geopandas

    top_areas = gdf_crimes_with_areas['pri_neigh'].value_counts().nlargest(15).index.tolist() ## Aqui se toman los 15 barrios con mas crimines
    
    return gdf_crimes_with_areas, gdf_bounds, top_areas

gdf_crimes, gdf_bounds, top_areas = load_data()

## Filtros
st.sidebar.header('Selección de Área y Tiempo')
st.sidebar.markdown("Elige un barrio y los años para un análisis detallado.")
selected_area = st.sidebar.selectbox(
    'Selecciona un Barrio para Analizar',
    options=['General (Toda la ciudad)'] + top_areas
)

available_years = sorted(gdf_crimes['Year'].unique(), reverse=True)
selected_years = st.sidebar.multiselect(
    'Selecciona Año(s)',
    options=available_years,
    default=[available_years[0]] if available_years else []
)

# Filtros
if selected_area == 'General (Toda la ciudad)':
    crimes_to_display = gdf_crimes
    area_to_highlight = None
else:
    crimes_to_display = gdf_crimes[gdf_crimes['pri_neigh'] == selected_area]
    area_to_highlight = gdf_bounds[gdf_bounds['pri_neigh'] == selected_area]

if selected_years:
    crimes_to_display = crimes_to_display[crimes_to_display['Year'].isin(selected_years)]


st.title('Dashboard de Análisis de Crímenes en Chicago')

col1, col2 = st.columns([2, 1])

# Mapa
with col1:
    st.subheader(f"Mapa de Crímenes: {selected_area}")
    
    m = folium.Map(location=[41.88, -87.63], zoom_start=10)

    for _, area in gdf_bounds.iterrows():
        is_selected = (area['pri_neigh'] == selected_area)
        style = {'color': 'red' if is_selected else 'blue', 'weight': 3 if is_selected else 1,
                 'fillOpacity': 0.4 if is_selected else 0.05, 'fillColor': 'red' if is_selected else 'blue'}
        folium.GeoJson(area.geometry, style_function=lambda x, style=style: style, tooltip=area['pri_neigh']).add_to(m)

    if area_to_highlight is not None and not area_to_highlight.empty:
        m.fit_bounds(area_to_highlight.geometry.total_bounds.tolist())

    marker_cluster = MarkerCluster().add_to(m)
    for _, crime in crimes_to_display.head(5000).iterrows(): 
        tooltip_text = f"<b>Tipo:</b> {crime['Primary Type']}<br><b>Lugar:</b> {crime['Location Description']}"
        folium.Marker(location=[crime['lat'], crime['lon']], tooltip=tooltip_text).add_to(marker_cluster)

    st_folium(m, width='100%', height=760, returned_objects=[])

# Metricas y Graficos
with col2:
    st.subheader(f"Análisis Detallado: {selected_area}")
    
    if selected_years:
        st.markdown(f"**Año(s) en análisis:** {', '.join(map(str, sorted(selected_years)))}")

    if not crimes_to_display.empty:
        total_crimes = len(crimes_to_display)
        most_frequent_crime = crimes_to_display['Primary Type'].mode()[0]
        most_frequent_location = crimes_to_display['Location Description'].mode()[0]
        
        st.metric("Total de Crímenes Registrados", f"{total_crimes:,}")
        st.metric("Crimen Más Frecuente", most_frequent_crime)
        st.metric("Lugar Más Común", most_frequent_location)
        st.markdown("---")

        st.markdown("##### Top 5 Tipos de Crímenes")
        crime_chart = alt.Chart(crimes_to_display['Primary Type'].value_counts().nlargest(5).reset_index()).mark_bar().encode(
            x=alt.X('count:Q', title='Número de Crímenes'), y=alt.Y('Primary Type:N', title='Tipo de Crimen', sort='-x')
        )
        st.altair_chart(crime_chart, use_container_width=True)

        st.markdown("##### Top 5 Lugares de Crímenes")
        location_chart = alt.Chart(crimes_to_display['Location Description'].value_counts().nlargest(5).reset_index()).mark_bar().encode(
            x=alt.X('count:Q', title='Número de Crímenes'), y=alt.Y('Location Description:N', title='Lugar del Crimen', sort='-x')
        )
        st.altair_chart(location_chart, use_container_width=True)
    else:
        st.warning("No se encontraron crímenes para el área y año(s) seleccionados.")

## DIAGRAMA DE SANKEY 
st.markdown("---")
st.subheader("Flujo de Delito a Arresto para el Área Seleccionada")

top_5_crimes = crimes_to_display['Primary Type'].value_counts().nlargest(5).index.tolist()
sankey_df = crimes_to_display[crimes_to_display['Primary Type'].isin(top_5_crimes)]

if not sankey_df.empty:
    sankey_data = sankey_df.groupby(['Primary Type', 'Arrest']).size().reset_index(name='count')

    labels = list(sankey_data['Primary Type'].unique()) + ['Con Arresto', 'Sin Arresto']
    source = [labels.index(cat) for cat in sankey_data['Primary Type']]
    target = [labels.index('Con Arresto') if arrest else labels.index('Sin Arresto') for arrest in sankey_data['Arrest']]
    value = sankey_data['count'] 

    
    # se crea una lista de colores para cada link
    link_colors = []
    for t in target:
        if labels[t] == 'Con Arresto':
            # Rojo para los links que terminan en 'Con Arresto'// Esto para una mejor vizualisación
            link_colors.append('rgba(255, 0, 0, 0.6)')
        else:
            # Gris para los links que terminan en 'Sin Arresto'
            link_colors.append('rgba(200, 200, 200, 0.6)')

    # se crea la figura pasando la lista de colores al link
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=30,
            thickness=20,
            line=dict(color="black", width=0.3),
            label=labels,
            
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color=link_colors ##  Lista de colores
        )
    )])
    fig.update_layout(title_text="Proporción de Arrestos por Tipo de Crimen", font_size=12, height=600)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay suficientes datos para generar el diagrama de flujo para esta selección.")