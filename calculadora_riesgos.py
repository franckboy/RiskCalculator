import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder

# Configuración de la página
st.set_page_config(layout="wide")

# Inicializar tabla de riesgos si no existe
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre", "Probabilidad", "Impacto", "Exposición", "Riesgo", "Tipo",
        "Amenaza", "Control", "Residual"
    ])

# Sidebar tipo dashboard
st.sidebar.title("Menú de Navegación")
seccion = st.sidebar.radio("Ir a", ["Formulario", "Matriz Acumulada", "Simulación Monte Carlo", "Mapas y Tablas"])

# FORMULARIO
if seccion == "Formulario":
    st.header("Formulario de Evaluación de Riesgos")
    with st.form("riesgo_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del Riesgo")
            probabilidad = st.slider("Probabilidad", 1, 5, 3)
            exposicion = st.slider("Exposición", 1, 5, 3)
        with col2:
            impacto = st.slider("Impacto", 1, 100, 50)
            tipo = st.selectbox("Tipo de Impacto", ["H", "E", "O", "A", "I", "T", "R", "C", "S"])
            amenaza = st.selectbox("Amenaza Deliberada", [1, 2, 3])
            control = st.slider("Efectividad de Control (%)", 0, 100, 50)
        enviar = st.form_submit_button("Agregar Riesgo")

    if enviar and nombre:
        riesgo = probabilidad * impacto
        residual = riesgo * (1 - control / 100) * amenaza * (exposicion / 5)
        nuevo = pd.DataFrame([[nombre, probabilidad, impacto, exposicion, riesgo, tipo, amenaza, control, residual]],
                              columns=st.session_state.riesgos.columns)
        if "Nombre" in st.session_state.riesgos.columns and nombre in st.session_state.riesgos["Nombre"].values:
            st.warning("Ese riesgo ya existe. Usa otro nombre o elimínalo primero.")
        else:
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, nuevo], ignore_index=True)
            st.success("Riesgo agregado correctamente")

# MATRIZ ACUMULADA
if seccion == "Matriz Acumulada":
    st.header("Matriz Acumulada de Riesgos")

    if not st.session_state.riesgos.empty:
        gb = GridOptionsBuilder.from_dataframe(st.session_state.riesgos)
        gb.configure_default_column(resizable=True, filter=True, sortable=True)
        grid_options = gb.build()
        AgGrid(st.session_state.riesgos, gridOptions=grid_options, height=300)

        st.subheader("Eliminar Riesgo")
        riesgo_borrar = st.text_input("Nombre del riesgo a eliminar")
        if st.button("Eliminar"):
            if "Nombre" in st.session_state.riesgos.columns and riesgo_borrar in st.session_state.riesgos["Nombre"].values:
                st.session_state.riesgos = st.session_state.riesgos[st.session_state.riesgos["Nombre"] != riesgo_borrar]
                st.success("Riesgo eliminado")
            else:
                st.warning("Nombre no encontrado")

        if st.button("Limpiar Matriz Acumulada"):
            st.session_state.riesgos = pd.DataFrame(columns=st.session_state.riesgos.columns)
            st.success("Matriz acumulada vaciada")
    else:
        st.info("No hay riesgos en la matriz acumulada.")

# SIMULACIÓN MONTE CARLO
if seccion == "Simulación Monte Carlo":
    st.header("Simulación Monte Carlo del Riesgo")

    n_iter = st.slider("Número de Iteraciones", 100, 10000, 1000)
    min_prob = st.slider("Probabilidad mínima", 1, 5, 1)
    max_prob = st.slider("Probabilidad máxima", 1, 5, 5)
    impacto_usuario = st.slider("Impacto fijo (aplicado a todas las simulaciones)", 1, 100, 50)

    resultados = []
    for _ in range(n_iter):
        prob = np.random.uniform(min_prob, max_prob)
        resultados.append(prob * impacto_usuario)

    st.write("---")
    st.subheader("Histograma del Riesgo Simulado")
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=resultados, nbinsx=50))
    st.plotly_chart(fig, use_container_width=True)

    st.write(f"**Promedio:** {np.mean(resultados):.2f} | **Máximo:** {np.max(resultados):.2f} | **Percentil 95:** {np.percentile(resultados, 95):.2f}")

# MAPAS Y TABLAS
if seccion == "Mapas y Tablas":
    st.header("Visualización de Datos de Riesgo")

    if not st.session_state.riesgos.empty:
        st.subheader("Mapa de Calor (Impacto vs Riesgo Residual)")
        heat_df = st.session_state.riesgos[["Impacto", "Residual"]].copy()

        fig = go.Figure(data=go.Heatmap(
            z=heat_df["Residual"],
            x=heat_df["Impacto"],
            y=heat_df["Impacto"],  # Para que se vea simétrico en ambas direcciones
            colorscale="YlOrRd"
        ))
        fig.update_layout(xaxis_title="Impacto", yaxis_title="Impacto", height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Gráfico de Barras - Riesgo Residual")
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=st.session_state.riesgos["Nombre"],
            y=st.session_state.riesgos["Residual"],
            marker_color='indianred'))
        fig2.update_layout(xaxis_title="Riesgo", yaxis_title="Residual")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Gráfico de Pareto")
        ordenado = st.session_state.riesgos.sort_values(by="Residual", ascending=False)
        ordenado["Acumulado"] = ordenado["Residual"].cumsum() / ordenado["Residual"].sum()

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=ordenado["Nombre"], y=ordenado["Residual"], name="Residual"))
        fig3.add_trace(go.Scatter(x=ordenado["Nombre"], y=ordenado["Acumulado"], name="% Acumulado", yaxis="y2"))
        fig3.update_layout(
            yaxis2=dict(overlaying='y', side='right', range=[0, 1]),
            yaxis=dict(title="Residual"),
            yaxis2_title="% Acumulado",
            title="Pareto de Riesgos"
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Agrega riesgos para ver visualizaciones.")
