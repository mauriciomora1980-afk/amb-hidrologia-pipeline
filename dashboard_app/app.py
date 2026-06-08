import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
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

m = folium.Map(location=[7.15, -73.07], zoom_start=12, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google')

for idx, row in data_mapa.iterrows():
    color = 'red' if row['Captación'] == st.session_state.seleccion else 'blue'
    folium.Marker(
        location=[row['lat'], row['lon']],
        popup=f"<b>{row['Captación']}</b><br>Lat: {row['lat']:.5f}<br>Lon: {row['lon']:.5f}",
        tooltip=row['Captación'],
        icon=folium.Icon(color=color, icon='tint', prefix='fa')
    ).add_to(m)

map_data = st_folium(m, width=700, height=500)

if map_data and map_data.get('last_object_clicked'):
    clicked_lat = map_data['last_object_clicked']['lat']
    clicked_lon = map_data['last_object_clicked']['lng']
    for idx, row in data_mapa.iterrows():
        if abs(clicked_lat - row['lat']) < 0.0005 and abs(clicked_lon - row['lon']) < 0.0005:
            st.session_state.seleccion = row['Captación']
            st.rerun()

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
    st.info(f"📍 Ubicacion: Lat {coord_actual['lat']:.6f}, Lon {coord_actual['lon']:.6f}")

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
                
                icono_path = f'assets/iconos/ico_{variable.lower()}.png'
                if os.path.exists(icono_path):
                    col_icono, col_titulo = st.columns([1, 5])
                    with col_icono:
                        st.image(icono_path, width=40)
                    with col_titulo:
                        st.markdown(f"### {variable}")
                else:
                    st.markdown(f"### {variable}")
                
                st.line_chart(data_filtered.set_index('Fecha')[variable], use_container_width=True)
                col_avg, col_min, col_max = st.columns(3)
                col_avg.metric("Promedio", f"{data_filtered[variable].mean():.2f}")
                col_min.metric("Mínimo", f"{data_filtered[variable].min():.2f}")
                col_max.metric("Máximo", f"{data_filtered[variable].max():.2f}")
            else:
                st.warning("No hay parámetros disponibles")
        else:
            st.warning(f"No hay datos para {st.session_state.seleccion}")

st.markdown("---")
st.caption(f"💧 Actualizado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")