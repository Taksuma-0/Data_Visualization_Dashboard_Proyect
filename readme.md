# Dashboard Interactivo de Criminalidad en Chicago (2012-2016)

Este proyecto presenta una aplicación web interactiva desarrollada con Streamlit para el análisis y la visualización de datos de incidentes criminales reportados en la ciudad de Chicago. La herramienta fue concebida para abordar el desafío de explorar un conjunto de datos masivo de una manera intuitiva. Se distingue por su **análisis multi-página**, un **mapa de hotspots interactivo**, y una suite de **filtros dinámicos** que actualizan todas las métricas y gráficos en tiempo real, ofreciendo una experiencia de usuario fluida y cohesiva.
---

## 📖 Descripción del Dashboard

La aplicación está estructurada como una experiencia guiada a través de tres páginas distintas, cada una diseñada con un propósito claro para facilitar el descubrimiento de insights.

La experiencia del usuario comienza en la **Página de Inicio**, que sirve como un portal introductorio. Esta página establece el contexto del proyecto, describe los objetivos del análisis, detalla la fuente y el alcance de los datos (periodo 2012-2016 del Chicago Data Portal) y presenta un importante descargo de responsabilidad sobre la naturaleza preliminar de la información. A partir de ahí, el usuario puede navegar a cualquiera de los dos paneles de análisis principales.

El panel de **Análisis Geográfico** es la herramienta central para la exploración espacial y está diseñado para responder a la pregunta fundamental: ***"¿Dónde ocurren los delitos?"***. A través de un mapa interactivo de Folium, el usuario puede seleccionar uno de los barrios con mayor incidencia criminal ("hotspots") desde un menú en la barra lateral. Al hacerlo, el mapa resalta dinámicamente el polígono del barrio seleccionado, ajusta el zoom y filtra los clusters de crímenes para mostrar únicamente los incidentes de esa zona y los años elegidos. Las métricas y gráficos en la columna derecha se actualizan simultáneamente, ofreciendo un perfil detallado del área seleccionada.

Para un análisis más profundo, la página de **Métricas Generales y Tendencias** permite responder a las preguntas ***"¿Qué delitos predominan y cómo evolucionan en el tiempo?"***. Este panel está dividido en secciones que permiten al usuario filtrar por un tipo de delito específico para ver sus métricas clave y la evolución de su tasa de arrestos año a año, o seleccionar un barrio para analizar su perfil delictivo particular, su tendencia histórica y su proporción de arrestos. Finalmente, incluye un gráfico de composición que compara visualmente el "ADN delictivo" de los barrios más afectados de la ciudad.

---

## 🛠️ Tecnologías y Datos

Para el desarrollo de este proyecto se utilizó un stack tecnológico moderno basado en **Python**. La aplicación web fue construida con **Streamlit**, mientras que la manipulación y el análisis de los datos, incluyendo la compleja unión espacial, se realizaron con **Pandas** y **GeoPandas**. Las visualizaciones geoespaciales se implementaron con **Folium** y sus plugins, y los gráficos dinámicos (barras, líneas, anillos y diagramas de Sankey) se crearon con las librerías **Altair** y **Plotly**. El análisis se basa en el conjunto de datos público del portal de Chicago, acotado al periodo **2012-2016** y contenido en los archivos `crimes_cleaned.csv` y `chicago_bounds.geojson`.

---

## ⚙️ Instalación y Ejecución Local

Para ejecutar este proyecto en tu máquina local, sigue estos pasos:

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/Taksuma-0/Data_Visualization_Dashboard_Proyect.git](https://github.com/Taksuma-0/Data_Visualization_Dashboard_Proyect.git)
    cd Data_Visualization_Dashboard_Proyect
    ```

2.  **Crea un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    source venv/bin/activate ## Esto linux, windows es diferente
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecuta la aplicación de Streamlit:**
    ```bash
    streamlit run 🏠_Inicio.py
    ```

