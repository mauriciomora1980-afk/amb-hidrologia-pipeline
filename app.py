import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(page_title="Gestión amb", layout="wide")

# Sidebar institucional
st.sidebar.image("/content/drive/MyDrive/Exposicion_Diana_Calderon/imagenes_estilizadas/logo_amb.png", width=200)
st.sidebar.title("Sistema de Monitoreo")

# Carga de datos maestros
ruta_csv = '/content/drive/MyDrive/Exposicion_Diana_Calderon/datos_procesados/MASTER_DATA_AMB.csv'
df = pd.read_csv(ruta_csv) if os.path.exists(ruta_csv) else None

# Selección de Captación
captaciones = ["Golondrinas", "Carrizal", "Arnania", "Surata", "Rio Frio"]
seleccion = st.sidebar.selectbox("Seleccione la Captación:", captaciones)

# Iconos
iconos = {
    "pH": "/content/drive/MyDrive/Exposicion_Diana_Calderon/imagenes_estilizadas/ico_ph.png",
    "Turbidez": "/content/drive/MyDrive/Exposicion_Diana_Calderon/imagenes_estilizadas/ico_turbiedad.png",
    "DBO": "/content/drive/MyDrive/Exposicion_Diana_Calderon/imagenes_estilizadas/ico_dbo.png",
    "Oxigeno": "/content/drive/MyDrive/Exposicion_Diana_Calderon/imagenes_estilizadas/ico_oxigeno.png",
    "Caudal": "/content/drive/MyDrive/Exposicion_Diana_Calderon/imagenes_estilizadas/ico_caudal.png"
}

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader(f"Infraestructura: {seleccion}")
    img_path = f'/content/drive/MyDrive/Exposicion_Diana_Calderon/imagenes_estilizadas/{seleccion.lower()}.png'
    if os.path.exists(img_path):
        st.image(img_path, use_container_width=True)
    else:
        st.write("Imagen institucional pendiente.")

with col2:
    if df is not None:
        variable = st.selectbox("Parámetro:", list(iconos.keys()))
        if variable in iconos:
            st.image(iconos[variable], width=60)
        
        data_filtered = df[df['Punto_Muestreo'] == seleccion]
        if not data_filtered.empty:
            st.line_chart(data_filtered.set_index('Fecha')[variable])
        else:
            st.info("Esperando carga de datos...")
