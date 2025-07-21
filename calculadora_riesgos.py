import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
import plotly.graph_objects as go

# Configuración inicial
st.set_page_config(layout="wide")
st.title("🧮 Evaluación de Riesgos")

# Inicializar la matriz de riesgos si no existe
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Riesgo", "Impacto", "Probabilidad", "Exposición", "Amenaza deliberada",
        "Índice de Criticidad", "Tipo de Impacto"
    ])

# --- FORMULARIO DE ENTRADA ---
with st.form("formulario_riesgo"):
    col1, col2, col3 = st.columns(3)

    with col1:
        riesgo = st.text_input("📝 Nombre del Riesgo").strip()
        tipo_impacto = st.selectbox("📌 Tipo de Impacto", ["H", "E", "O", "A", "I", "T", "R", "C", "S"])
        exposicion = st.slider("📊 Factor de Exposición", 1, 5, 3)

    with col2:
        impacto = st.slider("💥 Impacto", 1, 100, 50)
        probabilidad = st.slider("🎲 Probabilidad", 1, 100, 50)
        amenaza_deliberada = st.selectbox("⚠️ Amenaza Deliberada", [1, 2, 3])

    with col3:
        calcular = st.form_submit_button("➕ Agregar Riesgo")

# --- PROCESAMIENTO DEL FORMULARIO ---
if calcular:
    if riesgo == "":
        st.warning("Por favor ingresa un nombre para el riesgo.")
    elif riesgo in st.session_state.riesgos["Riesgo"].values:
        st.warning("Este riesgo ya ha sido agregado.")
    else:
        criticidad = impacto * probabilidad * exposicion * amenaza_deliberada
        nuevo = pd.DataFrame([{
            "Riesgo": riesgo,
            "Impacto": impacto,
            "Probabilidad": probabilidad,
            "Exposición": exposicion,
            "Amenaza deliberada": amenaza_deliberada,
            "Índice de Criticidad": criticidad,
            "Tipo de Impacto": tipo_impacto
        }])
        st.session_state.riesgos = pd.concat([st.session_state.riesgos, nuevo], ignore_index=True)
        st.success("✅ Riesgo agregado correctamente.")

# --- MATRIZ ACUMULADA + BOTONES ---
if not st.session_state.riesgos.empty:
    st.subheader("📋 Matriz Acumulada de Riesgos")

    # Tabla con AgGrid
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

    # Botón para eliminar un riesgo específico
    st.markdown("### Eliminar riesgo específico")
    riesgos_disponibles = st.session_state.riesgos["Riesgo"].unique().tolist()
    riesgo_a_eliminar = st.selectbox("Selecciona un riesgo para eliminar", riesgos_disponibles)

    if st.button("🗑️ Eliminar riesgo seleccionado"):
        st.session_state.riesgos = st.session_state.riesgos[st.session_state.riesgos["Riesgo"] != riesgo_a_eliminar]
        st.success(f"Riesgo '{riesgo_a_eliminar}' eliminado.")
        st.experimental_rerun()

    # Botón para limpiar todo
    if st.button("🧹 Limpiar matriz de riesgos"):
        st.session_state.riesgos = st.session_state.riesgos.iloc[0:0]
        st.experimental_rerun()

    # --- GRAFICAS ---
    st.markdown("## 📊 Análisis Visual de la Criticidad")

    col_g1, col_g2 = st.columns(2)

    # Gráfico de barras: Índice de Criticidad por Riesgo
    with col_g1:
        fig_barras = px.bar(
            st.session_state.riesgos,
            x="Riesgo",
            y="Índice de Criticidad",
            color="Tipo de Impacto",
            title="Índice de Criticidad por Riesgo"
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    # Mapa de calor (Probabilidad vs Impacto)
    with col_g2:
        fig_heatmap = go.Figure(
            data=go.Heatmap(
                z=st.session_state.riesgos["Índice de Criticidad"],
                x=st.session_state.riesgos["Probabilidad"],
                y=st.session_state.riesgos["Impacto"],
                colorscale="YlOrRd"
            )
        )
        fig_heatmap.update_layout(title="Mapa de Calor: Probabilidad vs Impacto", xaxis_title="Probabilidad", yaxis_title="Impacto")
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # Gráfico Pareto (riesgos ordenados)
    st.markdown("## 📈 Pareto de Riesgos")
    riesgos_ordenados = st.session_state.riesgos.sort_values(by="Índice de Criticidad", ascending=False)
    fig_pareto = px.bar(
        riesgos_ordenados,
        x="Riesgo",
        y="Índice de Criticidad",
        color="Tipo de Impacto",
        title="Análisis de Pareto"
    )
    st.plotly_chart(fig_pareto, use_container_width=True)
