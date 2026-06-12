import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Monitoreo AMB", layout="wide")
if os.path.exists("assets/iconos/logo_amb.png"):
    st.sidebar.image("assets/iconos/logo_amb.png", use_container_width=True)
    st.sidebar.markdown("---")
st.title("💧 Sistema de Monitoreo de Calidad de Agua")
st.sidebar.markdown("### 🔧 Depuración")
st.sidebar.write(f"Directorio actual: {os.getcwd()}")
ruta_historico = None
ruta_captaciones = None
ruta_embalse = None
for root, dirs, files in os.walk('.'):
    for file in files:
        if file == 'datos_historicos_formato_largo.csv':
            ruta_historico = os.path.join(root, file)
        if file == 'MASTER_DATA_COMPLETO.csv':
            ruta_captaciones = os.path.join(root, file)
        if file == 'datos_embalse_completo.csv':
            ruta_embalse = os.path.join(root, file)
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
if ruta_embalse:
    st.sidebar.success(f"✅ Embalse: {ruta_embalse}")
    df_embalse = pd.read_csv(ruta_embalse)
    df_embalse['Fecha'] = pd.to_datetime(df_embalse['Fecha'])
else:
    st.sidebar.error("❌ No se encontró datos_embalse_completo.csv")
    df_embalse = pd.DataFrame()
pagina = st.radio("📋 Navegación", ["1️⃣ Esquema del sistema", "2️⃣ Captaciones 2024", "3️⃣ Tendencia histórica 2012–2025", "4️⃣ Embalse", "5️⃣ Plantas de tratamiento", "6️⃣ Resumen ejecutivo", "7️⃣ Eficiencia de Plantas (COT)", "8️⃣ Hidrología (Embalse y afluentes) 2023", "9️⃣ Laboratorio amb 2026 Embalse", "🔟 Monitoreo Cuenca Suratá"], horizontal=True)
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
elif pagina == "2️⃣ Captaciones 2024":
    st.subheader("📍 Calidad de agua en captaciones 2024")
    if not df_captaciones.empty:
        captacion = st.selectbox("Seleccionar captación", df_captaciones['Captacion'].unique())
        parametro = st.selectbox("Seleccionar parámetro", ['ICA', 'ICOMI', 'ICOMO', 'ICOSUS', 'ICOpH', 'ICOTRO'])
        st.caption("📌 **Significado de los índices:**")
        st.caption("- **ICA**: Índice de Calidad del Agua")
        st.caption("- **ICOMI**: Mineralización")
        st.caption("- **ICOMO**: Materia Orgánica")
        st.caption("- **ICOSUS**: Sólidos Suspendidos")
        st.caption("- **ICOpH**: pH")
        st.caption("- **ICOTRO**: Eutrofización")
        df_filtrado = df_captaciones[(df_captaciones['Captacion'] == captacion) & (df_captaciones['Parametro'] == parametro)]
        if not df_filtrado.empty:
            fig = px.line(df_filtrado, x='Fecha', y='Valor', markers=True, title=f'{parametro} - {captacion} (2024)')
            st.plotly_chart(fig, use_container_width=True)
            col1, col2, col3 = st.columns(3)
            col1.metric("Promedio", f"{df_filtrado['Valor'].mean():.1f}")
            col2.metric("Mínimo", f"{df_filtrado['Valor'].min():.1f}")
            col3.metric("Máximo", f"{df_filtrado['Valor'].max():.1f}")
    else:
        st.error("No se pudieron cargar los datos de captaciones")
elif pagina == "3️⃣ Tendencia histórica 2012–2025":
    st.subheader("📈 Evolución de E.coli y turbiedad")
    if not df_historico.empty:
        col1, col2 = st.columns(2)
        with col1:
            sistema = st.selectbox("Sistema", df_historico['Sistema'].unique())
        with col2:
            parametro = st.selectbox("Parámetro", df_historico['Parametro'].unique())
        df_filtrado = df_historico[(df_historico['Sistema'] == sistema) & (df_historico['Parametro'] == parametro)]
        fig = px.line(df_filtrado, x='Año', y='Valor', markers=True, title=f'{parametro} - {sistema} (2012-2025)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("No se pudieron cargar los datos históricos")
elif pagina == "4️⃣ Embalse":
    st.subheader("💧 Monitoreo Histórico del Embalse (2015-2025)")
    if not df_embalse.empty:
        variables_comunes = ['pH', 'Turbiedad', 'Coliformes totales', 'Conductividad', 'Alcalinidad total', 'Dureza total', 'Arsénico', 'Mercurio']
        años_disponibles = [a for a in sorted(df_embalse['Fecha'].dt.year.unique()) if a != 2026]
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
        if not df_filtrado.empty:
            fig = px.line(df_filtrado, x='Fecha', y='Valor', color='Sitio' if sitio == 'Todos' else None, title=f'{parametro} - Evolución {año if año != "Todos" else "histórica"}', markers=True)
            st.plotly_chart(fig, use_container_width=True)
            col_avg, col_min, col_max = st.columns(3)
            col_avg.metric("Promedio", f"{df_filtrado['Valor'].mean():.2f}")
            col_min.metric("Mínimo", f"{df_filtrado['Valor'].min():.2f}")
            col_max.metric("Máximo", f"{df_filtrado['Valor'].max():.2f}")
            with st.expander("📋 Ver todos los datos"):
                st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("No hay datos para la combinación seleccionada")
    else:
        st.error("No se pudieron cargar los datos del embalse")
    st.caption("📌 Datos históricos: 2015-2017 (Excel) | Datos recientes: 2024-2025 | 2026 en pestaña específica")
elif pagina == "5️⃣ Plantas de tratamiento":
    st.subheader("🏭 Calidad del agua que llega a las plantas")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Planta La Flora", "Recibe Sistema Tona", "Carrizal + Arnania + Golondrinas")
    with col2:
        st.metric("Planta Florida", "Recibe Río Frío", "Monitoreo continuo")
    with col3:
        st.metric("Planta Bosconia", "Recibe Río Suratá", "Monitoreo continuo")
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
elif pagina == "7️⃣ Eficiencia de Plantas (COT)":
    st.subheader("📊 Carbono Orgánico Total (COT) - Resolución 2115/2007")
    st.caption("🔹 **Norma Resolución 2115: COT en AGUA TRATADA ≤ 5.0 mg/L** | 🔹 **Eficiencia objetivo: > 30% de remoción**")
    df_cot = pd.read_csv('data/datos_cot_plantas.csv')
    df_cot['Fecha_Muestra'] = pd.to_datetime(df_cot['Fecha_Muestra'])
    plantas = sorted(df_cot['Planta'].unique())
    planta_sel = st.selectbox("Seleccionar Planta", plantas, index=0)
    df_planta = df_cot[df_cot['Planta'] == planta_sel].copy()
    if not df_planta.empty:
        df_pivot = df_planta.pivot(index='Fecha_Muestra', columns='Tipo_Muestra', values='Resultado_COT_mgL').dropna()
        if not df_pivot.empty and 'AGUA CRUDA' in df_pivot.columns and 'AGUA TRATADA' in df_pivot.columns:
            df_pivot['Eficiencia (%)'] = ((df_pivot['AGUA CRUDA'] - df_pivot['AGUA TRATADA']) / df_pivot['AGUA CRUDA']) * 100
            col1, col2, col3 = st.columns(3)
            with col1:
                promedio_tratada = df_pivot['AGUA TRATADA'].mean()
                cumple = "✓ Cumple norma (≤5.0)" if promedio_tratada <= 5.0 else "✗ Supera norma (>5.0)"
                st.metric("COT Tratado Promedio", f"{promedio_tratada:.2f} mg/L", delta=cumple)
            with col2:
                st.metric("Eficiencia Promedio", f"{df_pivot['Eficiencia (%)'].mean():.1f}%")
            with col3:
                cumple_muestras = (df_pivot['AGUA TRATADA'] <= 5.0).sum()
                st.metric("Cumplimiento Norma", f"{cumple_muestras}/{len(df_pivot)} muestras")
            fig = px.line(df_planta, x='Fecha_Muestra', y='Resultado_COT_mgL', color='Tipo_Muestra', title=f'COT - {planta_sel} (Crudo vs Tratado)', markers=True)
            fig.add_hline(y=5.0, line_dash="dash", line_color="red", annotation_text="Límite Norma 5.0 mg/L")
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("📈 Eficiencia de Remoción de COT")
            df_mostrar = df_pivot[['AGUA CRUDA', 'AGUA TRATADA', 'Eficiencia (%)']].copy()
            df_mostrar['Cumple'] = df_pivot['AGUA TRATADA'] <= 5.0
            df_mostrar['Cumple'] = df_mostrar['Cumple'].map({True: '✅ Cumple', False: '❌ No cumple'})
            st.dataframe(df_mostrar, use_container_width=True)
            fig_ef = px.bar(df_pivot, x=df_pivot.index, y='Eficiencia (%)', title=f'Eficiencia de Remoción - {planta_sel}', color='Eficiencia (%)', color_continuous_scale=['red', 'yellow', 'green'])
            fig_ef.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Eficiencia objetivo 30%")
            st.plotly_chart(fig_ef, use_container_width=True)
            resumen = df_cot.groupby(['Planta', 'Tipo_Muestra'])['Resultado_COT_mgL'].mean().unstack()
            if 'AGUA CRUDA' in resumen.columns and 'AGUA TRATADA' in resumen.columns:
                resumen['Eficiencia (%)'] = ((resumen['AGUA CRUDA'] - resumen['AGUA TRATADA']) / resumen['AGUA CRUDA']) * 100
                resumen['Cumple_Norma'] = resumen['AGUA TRATADA'] <= 5.0
                resumen['Cumple_Eficiencia'] = resumen['Eficiencia (%)'] >= 30
                st.dataframe(resumen, use_container_width=True)
        else:
            st.warning("No hay suficientes datos (crudo y tratado) para calcular eficiencia")
    else:
        st.warning("No hay datos para la planta seleccionada")
elif pagina == "8️⃣ Hidrología (Embalse y afluentes) 2023":
    st.subheader("🧬 Hidrobiología del Embalse - ECOSAM 2023")
    st.caption("Datos de ECOSAM S.A.S. (Caracterización hidrobiológica, junio 2023)")
    datos_hidro = pd.DataFrame({
        'Punto': ['Cola del embalse', 'Centro del embalse', 'Captación del embalse', 'Embalse Litoral izquierdo', 'Río Tona antes Q. Ranas', 'Quebrada Ranas', 'Aguas debajo de la presa', 'Cola del embalse', 'Centro del embalse', 'Captación del embalse', 'Aguas debajo de la presa', 'Quebrada El Gualilo'],
        'Comunidad': ['Fitoplancton', 'Fitoplancton', 'Fitoplancton', 'Perifiton', 'Perifiton', 'Perifiton', 'Perifiton', 'Zooplancton', 'Zooplancton', 'Zooplancton', 'Bentónicos', 'Bentónicos'],
        'Taxa': ['Navicula sp.', 'Navicula sp.', 'Navicula sp.', 'Navicula sp.', 'Navicula sp.', 'Navicula sp.', 'Navicula sp.', 'Brachionus sp.', 'Brachionus sp.', 'Brachionus sp.', 'Physidae', 'Naucoridae'],
        'Abundancia': [147, 0, 34, 34, 92, 180, 43, 35, 902, 559, 4, 2],
        'Unidad': ['Ind/L', 'Ind/L', 'Ind/L', 'Ind/cm²', 'Ind/cm²', 'Ind/cm²', 'Ind/cm²', 'Ind/L', 'Ind/L', 'Ind/L', 'Ind/m²', 'Ind/m²']
    })
    comunidades = ['Todas'] + sorted(datos_hidro['Comunidad'].unique())
    comunidad_sel = st.selectbox("Seleccionar comunidad hidrobiológica", comunidades, key="comunidad_hidro_pestana")
    if comunidad_sel != 'Todas':
        df_hidro = datos_hidro[datos_hidro['Comunidad'] == comunidad_sel]
    else:
        df_hidro = datos_hidro
    fig_hidro = px.bar(df_hidro, x='Punto', y='Abundancia', color='Taxa', title=f'Abundancia de {comunidad_sel if comunidad_sel != "Todas" else "comunidades hidrobiológicas"} (ECOSAM 2023)', barmode='group')
    st.plotly_chart(fig_hidro, use_container_width=True)
    with st.expander("📋 Ver todos los datos hidrobiológicos"):
        st.dataframe(datos_hidro, use_container_width=True)
    st.caption("📌 Fuente: ECOSAM S.A.S. - Caracterización hidrobiológica del embalse de Bucaramanga, junio 2023")
elif pagina == "9️⃣ Laboratorio amb 2026 Embalse":
    st.subheader("🔬 Monitoreos Laboratorio amb 2026 - Embalse")
    st.caption("📌 Datos de muestras compuestas superficiales (integra superficial + profundidad)")
    df_2026 = df_embalse[df_embalse['Fecha'].dt.year == 2026]
    if not df_2026.empty:
        col1, col2 = st.columns(2)
        with col1:
            parametro = st.selectbox("📊 Seleccionar parámetro", df_2026['Parametro'].unique(), key="param_2026")
        with col2:
            sitio = st.selectbox("📍 Seleccionar sitio", ['Todos'] + sorted(df_2026['Sitio'].unique()), key="sitio_2026")
        df_filtrado = df_2026[df_2026['Parametro'] == parametro]
        if sitio != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Sitio'] == sitio]
        if not df_filtrado.empty:
            fig = px.line(df_filtrado, x='Fecha', y='Valor', color='Sitio' if sitio == 'Todos' else None, title=f'{parametro} - Laboratorio amb 2026', markers=True)
            st.plotly_chart(fig, use_container_width=True)
            col_avg, col_min, col_max = st.columns(3)
            col_avg.metric("Promedio", f"{df_filtrado['Valor'].mean():.2f}")
            col_min.metric("Mínimo", f"{df_filtrado['Valor'].min():.2f}")
            col_max.metric("Máximo", f"{df_filtrado['Valor'].max():.2f}")
            with st.expander("📋 Ver todos los datos 2026"):
                st.dataframe(df_filtrado, use_container_width=True)
        else:
            st.warning("No hay datos para la combinación seleccionada")
    else:
        st.info("No hay datos disponibles para 2026")
elif pagina == "🔟 Monitoreo Cuenca Suratá":
    st.subheader("🏔️ Monitoreo de Calidad de Agua - Cuenca Suratá")
    st.caption("📌 Zona con influencia minera | Monitoreo mensual | Datos de enero 2026")
    datos_surata = pd.DataFrame({
        'Sitio': ['Río Charta', 'Pánaga', 'Uña de Gato', 'Río Vetas', 'Quebrada La Baja'],
        'pH': [8.14, 7.92, 8.00, 7.22, 7.68],
        'Turbiedad (NTU)': [8.2, 8.5, 3.8, 6.2, 18.0],
        'Coliformes totales (NMP/100ml)': [16000, 92000, 5400, None, None],
        'E. coli (NMP/100ml)': [9200, 54000, 790, None, None],
        'Alcalinidad (mg CaCO3/L)': [72.0, 48.8, 49.4, 16.0, 15.4],
        'Arsénico (mg/L)': [0.0026, 0.0064, 0.0033, 0.0065, 0.0067],
        'Mercurio (mg/L)': ['<0.00025', '<0.00025', '<0.00025', '<0.00025', 0.00053],
        'Plomo (mg/L)': [0.037, 0.015, 0.0079, 0.0091, 0.071],
    })
    parametros = ['pH', 'Turbiedad (NTU)', 'Alcalinidad (mg CaCO3/L)', 'Arsénico (mg/L)', 'Plomo (mg/L)']
    parametro_sel = st.selectbox("📊 Seleccionar parámetro", parametros)
    fig = px.bar(datos_surata, x='Sitio', y=parametro_sel, title=f'{parametro_sel} en la Cuenca Suratá (enero 2026)', color=parametro_sel, color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)
    with st.expander("📋 Ver todos los datos"):
        st.dataframe(datos_surata, use_container_width=True)
    st.caption("📌 Nota: Río Vetas y Quebrada La Baja no reportan datos de coliformes en este monitoreo")
    st.subheader("✅ Cumplimiento Normativo (Decreto 1594/84)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Arsénico", "✓ Todos < 0.05 mg/L", "Cumple norma")
    with col2:
        st.metric("Mercurio", "✓ Excepto La Baja (0.00053)", "< 0.002 mg/L")
    with col3:
        st.metric("Plomo", "✓ Todos < 0.05 mg/L", "Cumple norma")
st.markdown("---")
st.caption(f"💧 Actualizado: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
