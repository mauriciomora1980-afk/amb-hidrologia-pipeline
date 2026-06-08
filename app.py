import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Gestión amb", layout="wide")

# Logo institucional
if os.path.exists("assets/iconos/logo_amb.png"):
    st.sidebar.image("assets/iconos/logo_amb.png", width=200)

st.title("💧 Sistema de Monitoreo de Captaciones - amb")

# Coordenadas
data_mapa = pd.DataFrame({
    'Captación': ["Golondrinas", "Carrizal", "Arnania", "Embalse", "Surata", "Rio Frio"],
    'lat': [7.17034, 7.17455, 7.17821, 7.15397, 7.15567, 7.07444],
    'lon': [-73.01967, -73.01392, -73.03096, -73.08964, -73.11143, -73.06694]
})

# Mapa Interactivo
st.subheader("Ubicación Geográfica de Captaciones")
fig = px.scatter_mapbox(data_mapa, lat="lat", lon="lon", hover_name="Captación", 
                        zoom=11, height=400, color_discrete_sequence=["#004a99"])
fig.update_layout(mapbox_style="satellite-streets", margin={"r":0,"t":0,"l":0,"b":0})

# Mostrar el mapa - eliminamos el on_select que no es válido
st.plotly_chart(fig, use_container_width=True)

# Estado de selección
if 'seleccion' not in st.session_state:
    st.session_state.seleccion = "Golondrinas"

# Selector en sidebar
seleccion = st.sidebar.selectbox("Captación:", data_mapa['Captación'].tolist(), 
                                 index=data_mapa['Captación'].tolist().index(st.session_state.seleccion))
st.session_state.seleccion = seleccion

# Datos
ruta_csv = 'data/MASTER_DATA_AMB.csv'
df = pd.read_csv(ruta_csv) if os.path.exists(ruta_csv) else None

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader(f"Infraestructura: {seleccion}")
    img_path = f'assets/iconos/{seleccion.lower()}.png'
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.info(f"No se encontró imagen para {seleccion}")

with col2:
    st.subheader("Análisis de Calidad")
    if df is not None:
        # Verificar que la columna 'Punto_Muestreo' existe
        if 'Punto_Muestreo' in df.columns:
            # Filtrar por la captación seleccionada
            data_filtered = df[df['Punto_Muestreo'] == seleccion]
            
            if not data_filtered.empty:
                # Obtener columnas numéricas para análisis
                cols = data_filtered.select_dtypes(include=['number']).columns.tolist()
                # Excluir columnas que no son parámetros de calidad (como IDs)
                cols = [col for col in cols if col not in ['ID', 'id', 'Index']]
                
                if cols:
                    variable = st.selectbox("Parámetro:", cols)
                    
                    # Mostrar ícono del parámetro si existe
                    icon_path = f'assets/iconos/ico_{variable.lower()}.png'
                    if os.path.exists(icon_path):
                        st.image(icon_path, width=60)
                    
                    # Gráfico de línea
                    st.line_chart(data_filtered.set_index('Fecha')[variable] if 'Fecha' in data_filtered.columns 
                                 else data_filtered[variable], use_container_width=True)
                    
                    # Mostrar estadísticas básicas
                    with st.expander("📊 Estadísticas"):
                        st.metric("Valor promedio", f"{data_filtered[variable].mean():.2f}")
                        st.metric("Valor mínimo", f"{data_filtered[variable].min():.2f}")
                        st.metric("Valor máximo", f"{data_filtered[variable].max():.2f}")
                else:
                    st.info("No hay parámetros numéricos para analizar.")
            else:
                st.info(f"No hay datos disponibles para {seleccion}.")
        else:
            st.error("La columna 'Punto_Muestreo' no existe en el archivo CSV. Verifica los nombres de las columnas.")
            st.write("Columnas disponibles:", df.columns.tolist())
    else:
        st.info(f"Esperando conexión a base de datos... No se encontró el archivo en: {ruta_csv}")
        st.write("Asegúrate de que el archivo MASTER_DATA_AMB.csv existe en la carpeta 'data/'")
