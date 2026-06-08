import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Gestión amb", layout="wide")

# Logo
st.sidebar.image("assets/iconos/logo_amb.png", width=200)

st.title("💧 Sistema de Monitoreo de Captaciones - amb")

# 1. Definir Coordenadas
data_mapa = pd.DataFrame({
    'Captación': ["Golondrinas", "Carrizal", "Arnania", "Embalse", "Surata", "Rio Frio"],
    'lat': [7.17034, 7.17455, 7.17821, 7.15397, 7.15567, 7.07444],
    'lon': [-73.01967, -73.01392, -73.03096, -73.08964, -73.11143, -73.06694]
})

# 2. Mapa Interactivo
st.subheader("Ubicación Geográfica de Captaciones")
fig = px.scatter_mapbox(data_mapa, lat="lat", lon="lon", hover_name="Captación", 
                        zoom=12, height=300, color_discrete_sequence=["#004a99"])
fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

# 3. Selección y Datos
st.markdown("---")
captaciones = data_mapa['Captación'].tolist()
seleccion = st.selectbox("Seleccione Captación para detalle técnico:", captaciones)

ruta_csv = 'data/MASTER_DATA_AMB.csv'
df = pd.read_csv(ruta_csv) if os.path.exists(ruta_csv) else None

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader(f"Infraestructura: {seleccion}")
    img_path = f'assets/iconos/{seleccion.lower()}.png'
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)

with col2:
    if df is not None:
        variable = st.selectbox("Parámetro a analizar:", df.select_dtypes(include=['number']).columns)
        data_filtered = df[df['Punto_Muestreo'] == seleccion]
        if not data_filtered.empty:
            st.line_chart(data_filtered.set_index('Fecha')[variable])
    else:
        st.info("Conectando con base de datos histórica...")
