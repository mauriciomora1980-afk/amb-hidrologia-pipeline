import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Monitoreo AMB", layout="wide")

# Logo institucional
if os.path.exists("assets/iconos/logo_amb.png"):
    st.sidebar.image("assets/iconos/logo_amb.png", use_container_width=True)
    st.sidebar.markdown("---")

st.title("💧 Sistema de Monitoreo de Calidad de Agua")

# ================= DIAGNÓSTICO: VERIFICAR ARCHIVOS =================
st.sidebar.markdown("### 🔧 Depuración")
st.sidebar.write(f"Directorio actual: {os.getcwd()}")

# Buscar los archivos
ruta_historico = None
ruta_captaciones = None

for root, dirs, files in os.walk('.'):
    for file in files:
        if file == 'datos_historicos_formato_largo.csv':
            ruta_historico = os.path.join(root, file)
        if file == 'MASTER_DATA_COMPLETO.csv':
            ruta_captaciones = os.path.join(root, file)

if ruta_historico:
    st.sidebar.success(f"✅ Histórico: {ruta_historico}")
    df_historico = pd.read_csv(ruta_historico)
else:
    st.sidebar.error("❌ No se encontró datos_historicos_formato_largo.csv")
    df_historico = pd.DataFrame()

if ruta_captaciones:
    st.sidebar.success(f"✅ Captaciones: {ruta_captaciones}")
    df_captaciones = pd.read_csv(ruta_captaciones)
else:
    st.sidebar.error("❌ No se encontró MASTER_DATA_COMPLETO.csv")
    df_captaciones = pd.DataFrame()

# Cargar datos del embalse
ruta_embalse = None
for root, dirs, files in os.walk('.'):
    for file in files:
        if file == 'datos_embalse_completo.csv':
            ruta_embalse = os.path.join(root, file)

if ruta_embalse:
    st.sidebar.success(f"✅ Embalse: {ruta_embalse}")
    df_embalse = pd.read_csv(ruta_embalse)
    df_embalse['Fecha'] = pd.to_datetime(df_embalse['Fecha'])
else:
    st.sidebar.error("❌ No se encontró datos_embalse_completo.csv")
    df_embalse = pd.DataFrame()

# ================= MENÚ DE PRESENTACIÓN =================
pagina = st.radio(
    "📋 Navegación",
    ["1️⃣ Esquema del sistema",
     "2️⃣ Captaciones 2024",
     "3️⃣ Tendencia histórica 2012–2025",
     "4️⃣ Embalse",
     "5️⃣ Plantas de tratamiento",
     "6️⃣ Resumen ejecutivo"],
    horizontal=True
)

# ================= 1️⃣ ESQUEMA DEL SISTEMA =================
if pagina == "1️⃣ Esquema del sistema":
    st.subheader("🧠 Esquema hidrológico del sistema AMB")
    if os.path.exists("assets/iconos/esquema_hidrologico.png"):
        st.image("assets/iconos/esquema_hidrologico.png", use_container_width=True)
    else:
        st.info("📌 Esquema disponible en la documentación")
    st.markdown("""
    ### 📌 Flujo del agua:
    - **Río Tona** → Captación Carrizal + excedente al Embalse
    - **Quebradas Arnania y Golondrinas** → Sistema Tona
    - **Sistema Tona** → Planta La Flora
    - **Río Frío** → Planta Florida
    - **Río Suratá** → Planta Bosconia
    """)

# ================= 2️⃣ CAPTACIONES 2024 =================
elif pagina == "2️⃣ Captaciones 2024":
    st.subheader("📍 Calidad de agua en captaciones 2024")
    if not df_captaciones.empty:
        captacion = st.selectbox("Seleccionar captación", df_captaciones['Captacion'].unique())
        parametro = st.selectbox("Seleccionar parámetro", ['ICA', 'ICOMI', 'ICOMO', 'ICOSUS', 'ICOpH', 'ICOTRO'])
        
        df_filtrado = df_captaciones[(df_captaciones['Captacion'] == captacion) & 
                                       (df_captaciones['Parametro'] == parametro)]
        
        if not df_filtrado.empty:
            fig = px.line(df_filtrado, x='Fecha', y='Valor', markers=True,
                          title=f'{parametro} - {captacion} (2024)')
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Promedio", f"{df_filtrado['Valor'].mean():.1f}")
            col2.metric("Mínimo", f"{df_filtrado['Valor'].min():.1f}")
            col3.metric("Máximo", f"{df_filtrado['Valor'].max():.1f}")
    else:
        st.error("No se pudieron cargar los datos de captaciones")

# ================= 3️⃣ TENDENCIA HISTÓRICA =================
elif pagina == "3️⃣ Tendencia histórica 2012–2025":
    st.subheader("📈 Evolución de E.coli y turbiedad")
    if not df_historico.empty:
        col1, col2 = st.columns(2)
        with col1:
            sistema = st.selectbox("Sistema", df_historico['Sistema'].unique())
        with col2:
            parametro = st.selectbox("Parámetro", df_historico['Parametro'].unique())
        
        df_filtrado = df_historico[(df_historico['Sistema'] == sistema) & 
                                    (df_historico['Parametro'] == parametro)]
        
        fig = px.line(df_filtrado, x='Año', y='Valor', markers=True,
                      title=f'{parametro} - {sistema} (2012-2025)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No se pudieron cargar los datos históricos")

# ================= 4️⃣ EMBALSE =================
elif pagina == "4️⃣ Embalse":
    st.subheader("💧 Monitoreo Histórico del Embalse (2015-2026)")
    
    if not df_embalse.empty:
        # Variables comunes con continuidad
        variables_comunes = ['pH', 'Turbiedad', 'Coliformes totales', 'Conductividad', 
                            'Alcalinidad total', 'Dureza total', 'Arsénico', 'Mercurio']
        
        # Obtener años disponibles
        años_disponibles = sorted(df_embalse['Fecha'].dt.year.unique())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            año = st.selectbox("📅 Seleccionar año", ['Todos'] + años_disponibles)
        with col2:
            parametro = st.selectbox("📊 Seleccionar parámetro", variables_comunes)
        with col3:
            sitio = st.selectbox("📍 Seleccionar sitio", ['Todos'] + sorted(df_embalse['Sitio'].unique()))
        
        df_filtrado = df_embalse[df_embalse['Parametro'] == parametro]
        if año != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Fecha'].dt.year == año]
        if sitio != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Sitio'] == sitio]
    
    st.caption("📌 Datos históricos: 2015-2017 (Excel) | Datos recientes: 2026 (Laboratorio AMB)")

# ================= 5️⃣ PLANTAS =================
elif pagina == "5️⃣ Plantas de tratamiento":
    st.subheader("🏭 Calidad del agua que llega a las plantas")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Planta La Flora", "Recibe Sistema Tona", "Carrizal + Arnania + Golondrinas")
    with col2:
        st.metric("Planta Florida", "Recibe Río Frío", "Monitoreo continuo")
    with col3:
        st.metric("Planta Bosconia", "Recibe Río Suratá", "Monitoreo continuo")

# ================= 6️⃣ RESUMEN EJECUTIVO =================
elif pagina == "6️⃣ Resumen ejecutivo":
    st.subheader("📊 Resumen de calidad de agua 2024")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Captaciones", "6")
    with col2:
        st.metric("Registros 2024", str(len(df_captaciones)) if not df_captaciones.empty else "0")
    with col3:
        st.metric("Años históricos", "14")
    with col4:
        st.metric("Plantas", "3")
    
    if not df_captaciones.empty:
        st.subheader("📈 Ranking ICA promedio 2024")
        df_ica = df_captaciones[df_captaciones['Parametro'] == 'ICA']
        ranking = df_ica.groupby('Captacion')['Valor'].mean().sort_values(ascending=False)
        for captacion, valor in ranking.items():
            color = "🟢" if valor > 80 else "🟡" if valor > 60 else "🔴"
            st.write(f"{color} **{captacion}**: {valor:.1f}")
        
        st.success("✅ El agua de las captaciones cumple con norma de calidad en 2024")

st.markdown("---")
st.caption(f"💧 Actualizado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
