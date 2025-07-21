import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
from st_aggrid import AgGrid, GridOptionsBuilder
import random

st.set_page_config(layout="wide")

# --- INICIALIZACIÓN DE VARIABLES ---
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre", "Tipo de Impacto", "Probabilidad", "Impacto",
        "Exposición", "Amenaza Deliberada", "Índice de Criticidad"
    ])

# --- DASHBOARD LATERAL ---
st.sidebar.title("📊 Panel de Control")

st.sidebar.markdown("### Bienvenido")
st.sidebar.info("Esta app evalúa riesgos conforme a ISO 31000 / 27001.")

# Limpiar TODOS los riesgos
if st.sidebar.button("🧹 Limpiar todos los riesgos"):
    st.session_state.riesgos = st.session_state.riesgos.iloc[0:0]
    st.experimental_rerun()

# Filtros
tipos_impacto = ["Todos", "Humano", "Económico", "Operacional", "Ambiental",
                 "Infraestructura", "Tecnológico", "Reputacional", "Comercial", "Social"]
impacto_filtro = st.sidebar.selectbox("Filtrar por impacto", tipos_impacto)

criticidad_minima = st.sidebar.slider("Filtrar por criticidad mínima", 0, 100, 0)

# Estadísticas
if not st.session_state.riesgos.empty:
    crits = st.session_state.riesgos["Índice de Criticidad"]
    st.sidebar.markdown("### 📈 Estadísticas")
    st.sidebar.write(f"Total riesgos: {len(crits)}")
    st.sidebar.write(f"Promedio criticidad: {crits.mean():.2f}")
    st.sidebar.write(f"Percentil 95: {np.percentile(crits, 95):.2f}")

# Exportar
def exportar_excel():
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    st.session_state.riesgos.to_excel(writer, index=False, sheet_name='Riesgos')
    writer.close()
    return output.getvalue()

if not st.session_state.riesgos.empty:
    st.sidebar.download_button("📤 Exportar a Excel", data=exportar_excel(), file_name="riesgos.xlsx")

# Selector de tema (estético, sin cambiar estilo aún)
st.sidebar.selectbox("🎨 Tema visual", ["Claro", "Oscuro", "Sistema"])

# --- FORMULARIO PRINCIPAL ---
st.title("🛡️ Evaluación de Riesgos")

with st.form("formulario_riesgo", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre del riesgo")
        tipo_impacto = st.selectbox("Tipo de Impacto", tipos_impacto[1:])
        amenaza_deliberada = st.selectbox("Amenaza Deliberada", [1, 2, 3])
    with col2:
        probabilidad = st.slider("Probabilidad", 1, 10)
        impacto = st.slider("Impacto", 1, 100)
        exposicion = st.slider("Exposición", 1, 5)

    agregar = st.form_submit_button("➕ Agregar Riesgo")

    if agregar:
        if not nombre:
            st.warning("Debes ingresar un nombre.")
        elif nombre in st.session_state.riesgos["Nombre"].values:
            st.warning("Ese riesgo ya existe.")
        else:
            criticidad = probabilidad * impacto * exposicion * amenaza_deliberada
            nuevo = pd.DataFrame([{
                "Nombre": nombre,
                "Tipo de Impacto": tipo_impacto,
                "Probabilidad": probabilidad,
                "Impacto": impacto,
                "Exposición": exposicion,
                "Amenaza Deliberada": amenaza_deliberada,
                "Índice de Criticidad": criticidad
            }])
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, nuevo], ignore_index=True)

# --- ELIMINACIÓN INDIVIDUAL ---
st.subheader("🗑️ Eliminar riesgo por nombre")

nombre_eliminar = st.text_input("Nombre exacto del riesgo a eliminar")
if st.button("❌ Eliminar"):
    if nombre_eliminar in st.session_state.riesgos["Nombre"].values:
        st.session_state.riesgos = st.session_state.riesgos[
            st.session_state.riesgos["Nombre"] != nombre_eliminar
        ]
        st.success("Riesgo eliminado.")
    else:
        st.warning("Ese nombre no se encuentra en la matriz.")

# --- MATRIZ ACTUAL ---
st.subheader("📋 Matriz Acumulada de Riesgos")

riesgos_mostrar = st.session_state.riesgos.copy()

if impacto_filtro != "Todos":
    riesgos_mostrar = riesgos_mostrar[riesgos_mostrar["Tipo de Impacto"] == impacto_filtro]
riesgos_mostrar = riesgos_mostrar[riesgos_mostrar["Índice de Criticidad"] >= criticidad_minima]

gb = GridOptionsBuilder.from_dataframe(riesgos_mostrar)
gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True)
grid_options = gb.build()

AgGrid(riesgos_mostrar, gridOptions=grid_options, fit_columns_on_grid_load=True, height=300, theme="alpine")

# --- MAPA DE CALOR ---
st.subheader("🔥 Mapa de Calor (Probabilidad vs Impacto)")

if not riesgos_mostrar.empty:
    heatmap_data = pd.pivot_table(
        riesgos_mostrar,
        values="Índice de Criticidad",
        index="Probabilidad",
        columns="Impacto",
        aggfunc="mean",
        fill_value=0
    )

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns.astype(str),
        y=heatmap_data.index.astype(str),
        colorscale="Reds"
    ))
    fig.update_layout(xaxis_title="Impacto", yaxis_title="Probabilidad")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Agrega riesgos para ver el mapa de calor.")

# --- SIMULACIÓN MONTE CARLO ---
st.subheader("🎲 Simulación Monte Carlo")

col_mc1, col_mc2, col_mc3 = st.columns(3)
with col_mc1:
    min_p = st.slider("Probabilidad mínima", 1, 10, 1)
    max_p = st.slider("Probabilidad máxima", 1, 10, 10)
with col_mc2:
    min_i = st.slider("Impacto mínimo", 1, 100, 10)
    max_i = st.slider("Impacto máximo", 1, 100, 100)
with col_mc3:
    iteraciones = st.number_input("Iteraciones", 100, 100000, 5000, step=500)

probs = np.random.uniform(min_p, max_p, iteraciones)
impacts = np.random.uniform(min_i, max_i, iteraciones)
resultados = probs * impacts

fig2 = go.Figure()
fig2.add_trace(go.Histogram(x=resultados, nbinsx=50, marker_color="indianred"))
fig2.update_layout(title="Distribución de Riesgo Simulado", xaxis_title="Riesgo", yaxis_title="Frecuencia")
st.plotly_chart(fig2, use_container_width=True)

st.write(f"Media: {np.mean(resultados):.2f}")
st.write(f"Máximo: {np.max(resultados):.2f}")
st.write(f"Percentil 95: {np.percentile(resultados, 95):.2f}")

