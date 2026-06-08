import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

st.set_page_config(page_title="Gestión amb", layout="wide")
st.title("💧 Sistema de Monitoreo de Captaciones - amb")

data_mapa = pd.DataFrame({
    'Captación': ["Golondrinas", "Carrizal", "Arnania", "Embalse", "Surata", "Rio Frio"],
    'lat': [7.17034, 7.17455, 7.17821, 7.15397, 7.15567, 7.07444],
    'lon': [-73.01967, -73.01392, -73.03096, -73.08964, -73.11143, -73.06694]
})

if 'seleccion' not in st.session_state:
    st.session_state.seleccion = "Golondrinas"

st.subheader("📍 Ubicación Geográfica de Captaciones")

fig = px.scatter_mapbox(
    data_mapa, lat="lat", lon="lon", hover_name="Captación",
    zoom=12, height=500, color_discrete_sequence=["#004a99"],
    size=[12]*len(data_mapa)
)
fig.update_traces(marker=dict(size=14, symbol="circle"))
fig.update_layout(
    mapbox_style="white-bg",
    mapbox_layers=[{
        "below": "traces",
        "sourcetype": "raster",
        "source": {
            "type": "raster",
            "tiles": ["https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]
        }
    }],
    mapbox=dict(center=dict(lat=7.15, lon=-73.07), zoom=12),
    margin={"r":0, "t":0, "l":0, "b":0}
)
st.plotly_chart(fig, use_container_width=True)

st.write("### 🗺️ Selecciona una captación:")
cols = st.columns(6)
for idx, captacion in enumerate(data_mapa['Captación'].tolist()):
    with cols[idx]:
        if st.button(f"📍 {captacion}", key=f"btn_{captacion}"):
            st.session_state.seleccion = captacion
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Captación Actual")
seleccion = st.sidebar.selectbox(
    "Seleccionar captación:", 
    data_mapa['Captación'].tolist(), 
    index=data_mapa['Captación'].tolist().index(st.session_state.seleccion)
)
if seleccion != st.session_state.seleccion:
    st.session_state.seleccion = seleccion
    st.rerun()
st.sidebar.success(f"✅ **{st.session_state.seleccion}**")

@st.cache_data
def cargar_datos():
    data_path = 'data/MASTER_DATA_AMB.csv'
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        st.sidebar.success(f"✅ Datos cargados: {len(df)} registros")
        return df
    return None

df = cargar_datos()
coord_actual = data_mapa[data_mapa['Captación'] == st.session_state.seleccion].iloc[0]
st.sidebar.caption(f"📍 {coord_actual['lat']:.5f}, {coord_actual['lon']:.5f}")

st.sidebar.markdown("---")
st.sidebar.subheader("🖼️ Vista de la Captación")
img_path = f'assets/iconos/{st.session_state.seleccion.lower()}.png'
if os.path.exists(img_path):
    st.sidebar.image(img_path, use_container_width=True)

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader(f"🏭 Infraestructura: {st.session_state.seleccion}")
    st.info(f"📍 **Ubicación**\nLatitud: {coord_actual['lat']:.6f}\nLongitud: {coord_actual['lon']:.6f}")

with col2:
    st.subheader("📊 Análisis de Calidad del Agua")
    if df is not None and 'Punto_Muestreo' in df.columns:
        data_filtered = df[df['Punto_Muestreo'] == st.session_state.seleccion].copy()
        if not data_filtered.empty:
            if 'Fecha' in data_filtered.columns:
                data_filtered['Fecha'] = pd.to_datetime(data_filtered['Fecha'])
                data_filtered = data_filtered.sort_values('Fecha')
            indicadores = ['ICA', 'ICOMI', 'ICOMO', 'ICOSUS', 'ICOpH', 'ICOTRO']
            parametros_disponibles = [p for p in indicadores if p in data_filtered.columns]
            if parametros_disponibles:
                variable = st.selectbox("📈 Parámetro de Calidad:", parametros_disponibles)
                if 'Fecha' in data_filtered.columns:
                    st.line_chart(data_filtered.set_index('Fecha')[variable], use_container_width=True)
                col_avg, col_min, col_max = st.columns(3)
                col_avg.metric("Promedio", f"{data_filtered[variable].mean():.2f}")
                col_min.metric("Mínimo", f"{data_filtered[variable].min():.2f}")
                col_max.metric("Máximo", f"{data_filtered[variable].max():.2f}")
            else:
                st.warning("No hay parámetros de calidad disponibles")
        else:
            st.warning(f"No hay datos para {st.session_state.seleccion}")

st.markdown("---")
st.caption(f"💧 Actualizado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")