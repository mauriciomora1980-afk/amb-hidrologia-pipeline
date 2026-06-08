import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestión amb", layout="wide")
# Usamos ruta relativa porque ya están en el repositorio
st.sidebar.image("assets/iconos/logo_amb.png", width=200)
st.title("💧 Sistema de Monitoreo - amb")

# Carga de datos desde carpeta local
ruta_csv = 'data/MASTER_DATA_AMB.csv'
df = pd.read_csv(ruta_csv) if os.path.exists(ruta_csv) else None

captaciones = ["Golondrinas", "Carrizal", "Arnania", "Surata", "Rio Frio"]
seleccion = st.sidebar.selectbox("Captación:", captaciones)

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader(f"Infraestructura: {seleccion}")
    img_path = f'assets/iconos/{seleccion.lower()}.png'
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)

with col2:
    st.subheader("Análisis de Calidad")
    if df is not None:
        variable = st.selectbox("Parámetro:", df.select_dtypes(include=['number']).columns)
        # Icono dinámico
        icon_path = f'assets/iconos/ico_{variable.lower()}.png'
        if os.path.exists(icon_path):
            st.image(icon_path, width=60)
        
        data_filtered = df[df['Punto_Muestreo'] == seleccion]
        if not data_filtered.empty:
            st.line_chart(data_filtered.set_index('Fecha')[variable])
    else:
        st.info("Datos cargados correctamente en el sistema.")
