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
                        zoom=11, height=300, color_discrete_sequence=["#004a99"])
fig.update_layout(mapbox_style="satellite-streets", margin={"r":0,"t":0,"l":0,"b":0})

# Usamos width='stretch' en lugar de use_container_width=True
event = st.plotly_chart(fig, width='stretch', on_select="rerun")

# Estado de selección
if 'seleccion' not in st.session_state:
    st.session_state.seleccion = "Golondrinas"

if event and "selection" in event and len(event["selection"]["points"]) > 0:
    st.session_state.seleccion = event["selection"]["points"][0]["hovertext"]

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
        st.image(img_path, width='stretch')

with col2:
    st.subheader("Análisis de Calidad")
    if df is not None:
        cols = df.select_dtypes(include=['number']).columns.tolist()
        if cols:
            variable = st.selectbox("Parámetro:", cols)
            icon_path = f'assets/iconos/ico_{variable.lower()}.png'
            if os.path.exists(icon_path):
                st.image(icon_path, width=60)
            
            data_filtered = df[df['Punto_Muestreo'] == seleccion]
            if not data_filtered.empty:
                st.line_chart(data_filtered.set_index('Fecha')[variable], width='stretch')
            else:
                st.info("No hay datos disponibles para esta captación.")
    else:
        st.info("Esperando conexión a base de datos...")
