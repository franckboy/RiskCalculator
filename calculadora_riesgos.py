import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.graph_objects as go
import random

# Configuración de página
st.set_page_config(layout="wide")

# Inicialización de estado de la matriz
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame()

# ---------- FORMULARIO ----------
st.title("Calculadora de Evaluación de Riesgos")

with st.form("formulario_riesgo"):
    col1, col2, col3 = st.columns(3)

    with col1:
        riesgo = st.text_input("Nombre del riesgo")
        amenaza_deliberada = st.selectbox("Amenaza deliberada", [1, 2, 3])
        exposicion = st.selectbox("Factor de exposición", [1, 2, 3, 4, 5])

    with col2:
        probabilidad = st.selectbox("Probabilidad", [1, 2, 3, 4, 5])
        efectividad = st.selectbox("Efectividad del control", [0.1, 0.3, 0.5, 0.7, 0.9])
        tipo_impacto = st.selectbox("Tipo de impacto", ["H", "E", "O", "A", "I", "T", "R", "C", "S"])

    with col3:
        # Slider de impacto individual (nuevo)
        impacto = st.slider("Impacto (1 a 100)", 1, 100, 50)

    submit = st.form_submit_button("Agregar riesgo")

# ---------- CÁLCULOS ----------
if submit and riesgo:
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    riesgo_residual = amenaza_residual * impacto * amenaza_deliberada

    nuevo_riesgo = pd.DataFrame([{
        "Riesgo": riesgo,
        "Amenaza Inherente": amenaza_inherente,
        "Efectividad": efectividad,
        "Amenaza Residual": amenaza_residual,
        "Impacto": impacto,
        "Amenaza Deliberada": amenaza_deliberada,
        "Riesgo Residual": riesgo_residual,
        "Tipo de Impacto": tipo_impacto,
        "Probabilidad": probabilidad,
        "Exposición": exposicion
    }])

    st.session_state.riesgos = pd.concat([st.session_state.riesgos, nuevo_riesgo], ignore_index=True)
    st.success("✅ Riesgo agregado correctamente.")

# ---------- TABLAS DE REFERENCIA ----------
st.subheader("Tablas de referencia")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Efectividad de controles", "Factor de Exposición", "Factor de Probabilidad",
    "Impacto/Severidad", "Índice de Criticidad", "Semáforo"
])

with tab1:
    st.markdown("Valores de efectividad de controles (0 = 100% efectivo)")
    st.table(pd.DataFrame({
        "Nivel": ["Muy alta", "Alta", "Media", "Baja", "Muy baja"],
        "Valor": [0.1, 0.3, 0.5, 0.7, 0.9]
    }))

with tab2:
    st.table(pd.DataFrame({
        "Descripción": ["Muy baja exposición", "Baja", "Media", "Alta", "Muy alta"],
        "Valor": [1, 2, 3, 4, 5]
    }))

with tab3:
    st.table(pd.DataFrame({
        "Frecuencia": ["Rara vez", "Ocasional", "Moderada", "Frecuente", "Casi seguro"],
        "Valor": [1, 2, 3, 4, 5]
    }))

with tab4:
    st.table(pd.DataFrame({
        "Tipo": ["H", "E", "O", "A", "I", "T", "R", "C", "S"],
        "Impacto ejemplo": ["Humano", "Económico", "Operacional", "Ambiental", "Infraestructura", "Tecnológico", "Reputacional", "Comercial", "Social"]
    }))

with tab5:
    st.markdown("Riesgo Residual = Amenaza Residual × Impacto × Amenaza Deliberada")

with tab6:
    st.markdown("Semáforo de criticidad:")
    st.markdown("""
    - 🟢 Riesgo bajo (< 300)
    - 🟡 Riesgo medio (300 - 700)
    - 🔴 Riesgo alto (> 700)
    """)

# ---------- MATRIZ DE RIESGOS ----------
if not st.session_state.riesgos.empty:
    st.subheader("Matriz acumulada de riesgos")

    # Mostrar matriz con AgGrid
    gb = GridOptionsBuilder.from_dataframe(st.session_state.riesgos)
    gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True)
    grid_options = gb.build()

    AgGrid(
        st.session_state.riesgos,
        gridOptions=grid_options,
        fit_columns_on_grid_load=True,
        height=300,
        theme="alpine"
    )

    # Botón para limpiar matriz
    if st.button("🧹 Limpiar matriz de riesgos"):
        st.session_state.riesgos = st.session_state.riesgos.iloc[0:0]
        st.experimental_rerun()

    # Eliminar riesgo individual
    st.markdown("### Eliminar riesgo específico")
    riesgos_disponibles = st.session_state.riesgos["Riesgo"].unique().tolist()
    riesgo_a_eliminar = st.selectbox("Selecciona un riesgo para eliminar", riesgos_disponibles)

    if st.button("🗑️ Eliminar riesgo seleccionado"):
        st.session_state.riesgos = st.session_state.riesgos[st.session_state.riesgos["Riesgo"] != riesgo_a_eliminar]
        st.success(f"Riesgo '{riesgo_a_eliminar}' eliminado.")
        st.experimental_rerun()

# ---------- MAPA DE CALOR ----------
if not st.session_state.riesgos.empty:
    st.subheader("Mapa de calor (Impacto vs Riesgo Residual)")
    data_heatmap = st.session_state.riesgos.copy()
    heatmap_data = data_heatmap.pivot_table(
        index="Impacto",
        columns="Probabilidad",
        values="Riesgo Residual",
        aggfunc="mean"
    )

    fig, ax = plt.subplots()
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax)
    ax.set_title("Mapa de calor del riesgo")
    st.pyplot(fig)

# ---------- GRÁFICO PARETO ----------
if not st.session_state.riesgos.empty:
    st.subheader("Gráfico de Pareto")

    pareto_df = st.session_state.riesgos.groupby("Riesgo")["Riesgo Residual"].sum().sort_values(ascending=False)
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(x=pareto_df.index, y=pareto_df.values, name="Riesgo Residual"))

    fig_pareto.update_layout(
        xaxis_title="Riesgo",
        yaxis_title="Riesgo Residual",
        title="Pareto de Riesgos",
        height=400
    )

    st.plotly_chart(fig_pareto, use_container_width=True)

# ---------- SIMULACIÓN MONTE CARLO ----------
st.subheader("Simulación Monte Carlo")

with st.expander("Configurar simulación"):
    n_iteraciones = st.slider("Número de iteraciones", 100, 10000, 1000, step=100)
    p_min = st.slider("Probabilidad mínima", 1, 5, 1)
    p_max = st.slider("Probabilidad máxima", 1, 5, 5)
    i_min = st.slider("Impacto mínimo", 1, 100, 10)
    i_max = st.slider("Impacto máximo", 1, 100, 90)

if st.button("🎲 Ejecutar simulación"):
    probabilidades = np.random.uniform(p_min, p_max, n_iteraciones)
    impactos = np.random.uniform(i_min, i_max, n_iteraciones)
    resultados = probabilidades * impactos

    promedio = np.mean(resultados)
    p95 = np.percentile(resultados, 95)
    st.write(f"**Promedio del riesgo:** {promedio:.2f}")
    st.write(f"**Percentil 95:** {p95:.2f}")

    fig_sim = go.Figure()
    fig_sim.add_trace(go.Histogram(x=resultados, nbinsx=50, name="Simulación"))
    fig_sim.update_layout(title="Histograma de Riesgo Simulado", xaxis_title="Riesgo", yaxis_title="Frecuencia")
    st.plotly_chart(fig_sim, use_container_width=True)
