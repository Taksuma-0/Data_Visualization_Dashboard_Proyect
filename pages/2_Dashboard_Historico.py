import streamlit as st
import pandas as pd
import geopandas as gpd
import altair as alt


st.set_page_config(
    page_title="Métricas Generales",
    page_icon="🔎",
    layout="wide"
)

## Carga de datos y limpieza como tal fina
@st.cache_data
def load_data():
    """Carga los datos y los une con los barrios."""
    gdf_bounds = gpd.read_file('chicago_bounds.geojson')
    df = pd.read_parquet('data/crimes_cleaned.parquet')
    
    df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True, errors='ignore')
    df.rename(columns={'Latitude': 'lat', 'Longitude': 'lon'}, inplace=True, errors='ignore')

    df.dropna(subset=['lat', 'lon'], inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df = df[df['Year'] != 2017] ### Eliminamos 2017 por los pocos datos

    gdf_crimes = gpd.GeoDataFrame(
        df, 
        geometry=gpd.points_from_xy(df.lon, df.lat), 
        crs=gdf_bounds.crs
    )
    
    gdf_crimes_with_areas = gpd.sjoin(gdf_crimes, gdf_bounds, how="inner", predicate='within')
    
    return gdf_crimes_with_areas


gdf_crimes = load_data()

st.title("🔎 Métricas Generales de Criminalidad")
st.markdown("Selecciona un tipo de delito o un barrio para ver estadísticas clave y tendencias.")

st.markdown("---")
## Analisis por tipo de delito
st.header("Análisis por Tipo de Delito abarcando [2012-2016]")

crime_types = sorted(gdf_crimes['Primary Type'].unique())
selected_crime = st.selectbox(
    'Selecciona un tipo de delito para analizar:',
    options=crime_types,
    index=crime_types.index('THEFT')  ## Se usa por Default THEFT
)

if selected_crime:
    crime_df = gdf_crimes[gdf_crimes['Primary Type'] == selected_crime]
    
    ## Metricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        arrest_rate = crime_df['Arrest'].mean() * 100
        st.metric("Tasa de Arresto (Total)", f"{arrest_rate:.1f}%")
    with col2:
        top_location = crime_df['Location Description'].mode()[0]
        st.metric("Lugar Más Común", top_location)
    with col3:
        top_community = crime_df['pri_neigh'].mode()[0]
        st.metric("Barrio Más Afectado", top_community)
    with col4:
        peak_year = crime_df['Year'].mode()[0]
        st.metric("Año con Mayor Incidencia", str(peak_year))

    st.markdown("##### Proporción de Arrestos por Año")

    ## Creamos los anillos
    years_to_display = [2012, 2013, 2014, 2015, 2016] ## años 
    cols = st.columns(5)

    for i, year in enumerate(years_to_display):
        with cols[i]:
            st.markdown(f"<h5 style='text-align: center; font-weight: bold;'>{year}</h5>", unsafe_allow_html=True)
            
            year_df = crime_df[crime_df['Year'] == year]
            total_crimes_year = len(year_df)
            
            if total_crimes_year > 0:
                arrest_data = year_df['Arrest'].value_counts().reset_index()
                arrest_data.columns = ['Arrest', 'count']
                arrest_data['Resultado'] = arrest_data['Arrest'].map({True: 'Arresto', False: 'No Arresto'})
                
                base = alt.Chart(arrest_data).transform_joinaggregate(
                    total='sum(count)' ## Suma de crimenes por año seleccionado
                ).transform_calculate(
                    percentage='datum.count / datum.total' ## Calculo del porcentaje
                ).encode(
                    theta=alt.Theta(field="count", type="quantitative", stack=True),
                    color=alt.Color(field="Resultado", type="nominal", title="Resultado",
                                    scale=alt.Scale(domain=['Arresto', 'No Arresto'], range=['#E45756', '#1f77b4'])),
                    tooltip=['Resultado', 'count', alt.Tooltip('percentage:Q', title='Porcentaje', format='.1%')]
                )
                
                ## Lo siguiente es para personalizar los graficos de pastel
                pie = base.mark_arc(
                innerRadius=45,     # Radio interior
                outerRadius=90,     # Radio exterior
                cornerRadius=1,    # Esquinas redondeadas
                stroke='white',     # Borde blanco entre segmentos
                strokeWidth=2       # Grosor del borde
                )
                
                text = base.mark_text(
                    radius=60, 
                    size=18, 
                    fontWeight='bold', 
                    color='white',       # Color del texto blanco
                    stroke='black',      # Color del contorno negro
                    strokeWidth=0.9      # Grosor del contorno
                ).encode(
                    # Usa el campo 'percentage' calculado y lo formatea sin decimales
                    text=alt.Text('percentage:Q', format='.0%')
                ).transform_filter(
                    alt.datum.percentage > 0.01 ## Oculta porcentajes muy pequeños para no solapar
                )

                final_chart = (pie + text).configure_legend(disable=True)
                
                st.altair_chart(final_chart, use_container_width=True)
                
                legend_html = f"""
                <div style="display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: -20px;">
                    <div>
                        <div style="display: flex; align-items: center; font-size: 12px;">
                            <span style="height: 10px; width: 10px; background-color: #E45756; border-radius: 50%; display: inline-block; margin-right: 5px;"></span>
                            Arresto
                        </div>
                        <div style="display: flex; align-items: center; font-size: 12px;">
                            <span style="height: 10px; width: 10px; background-color: #1f77b4; border-radius: 50%; display: inline-block; margin-right: 5px;"></span>
                            No Arresto
                        </div>
                    </div>
                    <div style="font-weight: bold; font-size: 14px;">
                        Total: {total_crimes_year:,}
                    </div>
                </div>
                """
                st.markdown(legend_html, unsafe_allow_html=True)
                
            else:
                st.markdown(f"<p style='text-align: center; font-weight: bold;'>{year}</p>", unsafe_allow_html=True)
                st.info("Sin datos")
st.markdown("---")

## Analisis por Barrio seleccionado por el Usuario
st.header("Análisis por Barrio abarcando [2012-2016]")

community_list = sorted(gdf_crimes['pri_neigh'].unique())
selected_community = st.selectbox(
    'Selecciona un barrio para analizar:',
    options=community_list,
    index=0 
)

if selected_community:
    community_df = gdf_crimes[gdf_crimes['pri_neigh'] == selected_community]
    
    st.subheader(f"Métricas para {selected_community}")
    col1, col2 = st.columns(2)
    
    with col1:
        # metricas principales
        total_crimes_in_community = len(community_df)
        top_crime_in_community = community_df['Primary Type'].mode()[0]
        peak_year_in_community = community_df['Year'].mode()[0]

        st.metric("Total de Crímenes Registrados", f"{total_crimes_in_community:,}")
        st.metric("Crimen Más Común", top_crime_in_community)
        st.metric("Año con Mayor Actividad", str(peak_year_in_community))

    with col2:
        # metricas de desglose de arrestos
        st.subheader("Desglose de Arrestos")
        arrest_count = int(community_df['Arrest'].sum())
        no_arrest_count = total_crimes_in_community - arrest_count
        
        st.metric("Casos CON Arresto", f"{arrest_count:,}")
        st.metric("Casos SIN Arresto", f"{no_arrest_count:,}")

    st.markdown("---")
    
    st.subheader("Visualizaciones para el Barrio Seleccionado")
    
    graph_col1, graph_col2 = st.columns(2)

    with graph_col1:
        st.markdown("###### Tendencia Histórica")
        yearly_crimes = community_df.groupby('Year').size().reset_index(name='count')
        
        base = alt.Chart(yearly_crimes).encode(
            x=alt.X('Year:O', title=str(peak_year_in_community), axis=alt.Axis(labelAngle=0))
        )
        
        area = base.mark_area(
            opacity=0.3,
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#1f77b4', offset=0), alt.GradientStop(color='white', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        )
        
        # Capa de la línea
        line = base.mark_line(color='#1f77b4', strokeWidth=3)
        
        # Capa de los puntos
        points = base.mark_point(size=70, color='#1f77b4', filled=True)

        # Combinar las capas
        trend_chart = (area + line + points).encode(
            y=alt.Y('count:Q', title='Número de Crímenes')
        ).properties(
            title="Evolución de la criminalidad"
        )
        st.altair_chart(trend_chart, use_container_width=True)

    with graph_col2:
        ## Grafico de anillo propio para esta vizualisación
        st.markdown("###### Proporción de Arrestos")
        arrest_data = community_df['Arrest'].value_counts().reset_index()
        arrest_data.columns = ['Arrest', 'count']
        arrest_data['Resultado'] = arrest_data['Arrest'].map({True: 'Arresto', False: 'No Arresto'})
        
        base_pie = alt.Chart(arrest_data).transform_joinaggregate(
            total='sum(count)'
        ).transform_calculate(
            percentage='datum.count / datum.total'
        ).encode(
            theta=alt.Theta(field="count", type="quantitative"),
            color=alt.Color(field="Resultado", type="nominal", title="Resultado",
                            scale=alt.Scale(domain=['Arresto', 'No Arresto'], range=['#E45756', '#1f77b4'])),
            tooltip=['Resultado', 'count', alt.Tooltip('percentage:Q', title='Porcentaje', format='.1%')]
        )
        
        ## Lo siguiente es para personalizar el grafico de pastel
        pie = base_pie.mark_arc(
            innerRadius=50, outerRadius=120,
            cornerRadius=1, stroke='white', strokeWidth=1
        )
        
        text = base.mark_text(
                    radius=60, 
                    size=18, 
                    fontWeight='bold', 
                    color='white',       # Color del texto blanco
                    stroke='black',      # Color del contorno negro
                    strokeWidth=0.9      # Grosor del contorno
                ).encode(
                    # Usa el campo 'percentage' calculado y lo formatea sin decimales
                    text=alt.Text('percentage:Q', format='.0%')
                ).transform_filter(
                    alt.datum.percentage > 0 # Oculta porcentajes muy pequeños para no solapar
                )

        pie_chart = (pie + text).properties(
            title="Proporción de Casos con/sin Arresto"
        ).configure_legend(disable=False)
        st.altair_chart(pie_chart, use_container_width=True)

st.markdown("---")

# Grafico general sobre los Barrios con mayor cantidad de crimenes Tomando todos los años
st.header("Composición del Crimen en Barrios con Mayor Actividad")
st.markdown("Compara el volumen y el tipo de crímenes en los 7 barrios más afectados.")

top_7_hoods = gdf_crimes['pri_neigh'].value_counts().nlargest(7).index.tolist()
composition_df = gdf_crimes[gdf_crimes['pri_neigh'].isin(top_7_hoods)]

chart_data = composition_df[['pri_neigh', 'Primary Type']]

composition_chart = alt.Chart(chart_data).mark_bar().encode(
    x=alt.X('count():Q', title='Número Total de Crímenes'),
    y=alt.Y('pri_neigh:N', title='Barrio', sort='-x'),
    color=alt.Color('Primary Type:N', title='Tipo de Crimen', scale=alt.Scale(scheme='tableau20')),
    tooltip=['pri_neigh', 'Primary Type', 'count()']
).properties(
    title='Composición de Crímenes por Barrio'
)
st.altair_chart(composition_chart, use_container_width=True)