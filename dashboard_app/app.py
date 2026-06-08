import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

st.set_page_config(page_title="Gestión amb", layout="wide")

st.title("💧 Sistema de Monitoreo de Captaciones - amb")

# Coordenadas
data_mapa = pd.DataFrame({
    'Captación': ["Golondrinas", "Carrizal", "Arnania", "Embalse", "Surata", "Rio Frio"],
    'lat': [7.17034, 7.17455, 7.17821, 7.15397, 7.15567, 7.07444],
    'lon': [-73.01967, -73.01392, -73.03096, -73.08964, -73.11143, -73.06694]
})

# Estado de selección
if 'seleccion' not in st.session_state:
    st.session_state.seleccion = "Golondrinas"

st.subheader("📍 Ubicación Geográfica de Captaciones")

# Mapa interactivo
fig = px.scatter_mapbox(
    data_mapa, 
    lat="lat", 
    lon="lon", 
    hover_name="Captación",
    hover_data={"lat": ":.5f", "lon": ":.5f"},
    zoom=12, 
    height=500,
    color_discrete_sequence=["#004a99"],
    size=[12]*len(data_mapa)
)

fig.update_traces(
    marker=dict(size=14, symbol="circle"),
    selector=dict(mode='markers')
)

fig.update_layout(
    mapbox_style="stamen-terrain",
    mapbox=dict(
        center=dict(lat=7.15, lon=-73.07),
        zoom=12
    ),
    margin={"r":0, "t":0, "l":0, "b":0},
    hovermode='closest'
)

st.plotly_chart(fig, use_container_width=True)

# Botones rápidos
st.write("### 🗺️ Selecciona una captación:")
cols = st.columns(6)
for idx, captacion in enumerate(data_mapa['Captación'].tolist()):
    with cols[idx]:
        if st.button(f"📍 {captacion}", key=f"btn_{captacion}"):
            st.session_state.seleccion = captacion
            st.rerun()

# Sidebar
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

# Cargar datos
@st.cache_data
def cargar_datos():
    # Buscar en la ubicación correcta dentro del contenedor
    data_path = 'data/MASTER_DATA_AMB.csv'
    
    if os.path.exists(data_path):
        try:
            df = pd.read_csv(data_path)
            st.sidebar.success(f"✅ Datos cargados: {len(df)} registros")
            return df
        except Exception as e:
            st.sidebar.error(f"Error al leer datos: {e}")
    
    # Si no hay datos, crear de ejemplo
    st.sidebar.warning("⚠️ Usando datos de demostración")
    return crear_datos_demo()

def crear_datos_demo():
    fechas = pd.date_range('2024-01-01', periods=30, freq='D')
    datos = []
    for captacion in data_mapa['Captación']:
        for i, fecha in enumerate(fechas):
            datos.append({
                'Punto_Muestreo': captacion,
                'Fecha': fecha,
                'Temperatura': 22 + np.random.normal(0, 2),
                'pH': 7.0 + np.random.normal(0, 0.2),
                'Oxigeno': 6.5 + np.random.normal(0, 0.5),
                'Turbiedad': 5 + np.random.normal(0, 1)
            })
    return pd.DataFrame(datos)

df = cargar_datos()

# Mostrar coordenadas
coord_actual = data_mapa[data_mapa['Captación'] == st.session_state.seleccion].iloc[0]
st.sidebar.caption(f"📍 {coord_actual['lat']:.5f}, {coord_actual['lon']:.5f}")

# Layout principal
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader(f"🏭 Infraestructura: {st.session_state.seleccion}")
    st.info(f"""
    📍 **Ubicación**  
    Latitud: {coord_actual['lat']:.6f}  
    Longitud: {coord_actual['lon']:.6f}
    """)

with col2:
    st.subheader("📊 Análisis de Calidad del Agua")
    
    if 'Punto_Muestreo' in df.columns:
        data_filtered = df[df['Punto_Muestreo'] == st.session_state.seleccion].copy()
        
        if not data_filtered.empty:
            if 'Fecha' in data_filtered.columns:
                data_filtered['Fecha'] = pd.to_datetime(data_filtered['Fecha'])
                data_filtered = data_filtered.sort_values('Fecha')
            
            numeric_cols = data_filtered.select_dtypes(include=['number']).columns.tolist()
            
            if numeric_cols:
                variable = st.selectbox("📈 Parámetro:", numeric_cols)
                
                if 'Fecha' in data_filtered.columns:
                    st.line_chart(data_filtered.set_index('Fecha')[variable], use_container_width=True)
                else:
                    st.bar_chart(data_filtered[variable], use_container_width=True)
                
                col_avg, col_min, col_max = st.columns(3)
                col_avg.metric("Promedio", f"{data_filtered[variable].mean():.2f}")
                col_min.metric("Mínimo", f"{data_filtered[variable].min():.2f}")
                col_max.metric("Máximo", f"{data_filtered[variable].max():.2f}")
                
                # Mostrar tabla
                with st.expander("📋 Ver todos los datos"):
                    st.dataframe(data_filtered, use_container_width=True)
            else:
                st.warning("No hay datos numéricos para analizar")
        else:
            st.warning(f"No hay datos para {st.session_state.seleccion}")
            st.info("Verifica que los nombres en 'Punto_Muestreo' coincidan exactamente")

st.markdown("---")
st.caption(f"💧 Sistema de Monitoreo - Actualizado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
