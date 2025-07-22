import streamlit as st
import pandas as pd
import numpy as np
from calculations import calcular_riesgo_residual, calcular_criticidad, clasificar_criticidad, clasificar_aceptabilidad
from calculations import generar_estadisticas_montecarlo, simular_montecarlo
from plotting import generar_grafico_pareto, generar_matriz_acumulada, generar_histograma
from utils import reset_form_fields, format_risk_dataframe
from data_config import textos, tipos_riesgo, niveles_probabilidad, niveles_exposicion, niveles_impacto, criticidad_límites

st.set_page_config(layout="wide")
st.title("Calculadora de Riesgos - ISO 31000 + ASIS")

# Inicialización de variables de estado
if "df_riesgos" not in st.session_state:
    st.session_state.df_riesgos = pd.DataFrame(columns=[
        "Nombre", "Descripción", "Tipo", "Probabilidad", "Exposición",
        "Impacto", "Efectividad del Control", "Amenaza Deliberada",
        "Riesgo Residual", "Índice de Criticidad", "Clasificación", "Aceptabilidad"
    ])
    st.session_state["current_edit_index"] = -1

# Valores por defecto
st.session_state.setdefault('default_type_impact', tipos_riesgo[0])
st.session_state.setdefault('default_probabilidad', niveles_probabilidad[0])
st.session_state.setdefault('default_exposicion', niveles_exposicion[0])
st.session_state.setdefault('default_impacto_numerico', 50)
st.session_state.setdefault('default_control_effectiveness', 0.5)

# ---- FORMULARIO PRINCIPAL ----
with st.form("formulario_riesgo"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre del riesgo", key="risk_name_input")
        descripcion = st.text_area("Descripción", key="risk_description_input")
        tipo = st.selectbox("Tipo de riesgo", tipos_riesgo, key="selected_type_impact")
        probabilidad = st.selectbox("Probabilidad", niveles_probabilidad, key="selected_probabilidad")
        exposicion = st.selectbox("Exposición", niveles_exposicion, key="selected_exposicion")
    with col2:
        impacto = st.slider("Impacto numérico (1-100)", 1, 100, key="impacto_numerico_slider")
        efectividad_control = st.slider("Efectividad del control (0.0 = sin control, 1.0 = control perfecto)", 0.0, 1.0, 0.5, key="control_effectiveness_slider")
        amenaza_deliberada = st.checkbox("¿Amenaza deliberada?", key="deliberate_threat_checkbox")

    submit = st.form_submit_button("Agregar/Actualizar Riesgo")

# ---- LÓGICA DE FORMULARIO ----
if submit:
    riesgo_residual = calcular_riesgo_residual(probabilidad, exposicion, impacto, efectividad_control)
    criticidad = calcular_criticidad(riesgo_residual, amenaza_deliberada)
    clasificacion = clasificar_criticidad(criticidad)
    aceptabilidad = clasificar_aceptabilidad(criticidad)

    nuevo_riesgo = pd.DataFrame([{
        "Nombre": nombre,
        "Descripción": descripcion,
        "Tipo": tipo,
        "Probabilidad": probabilidad,
        "Exposición": exposicion,
        "Impacto": impacto,
        "Efectividad del Control": efectividad_control,
        "Amenaza Deliberada": amenaza_deliberada,
        "Riesgo Residual": riesgo_residual,
        "Índice de Criticidad": criticidad,
        "Clasificación": clasificacion,
        "Aceptabilidad": aceptabilidad
    }])

    if st.session_state.current_edit_index >= 0:
        st.session_state.df_riesgos.iloc[st.session_state.current_edit_index] = nuevo_riesgo.iloc[0]
    else:
        st.session_state.df_riesgos = pd.concat([st.session_state.df_riesgos, nuevo_riesgo], ignore_index=True)

    reset_form_fields()

# ---- TABLA DE RIESGOS ----
if not st.session_state.df_riesgos.empty:
    st.subheader("Listado de Riesgos")
    st.dataframe(format_risk_dataframe(st.session_state.df_riesgos))

# ---- GRÁFICOS Y ANÁLISIS ----
if not st.session_state.df_riesgos.empty:
    st.subheader("Gráficos")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(generar_grafico_pareto(st.session_state.df_riesgos), use_container_width=True)
    with col2:
        st.plotly_chart(generar_matriz_acumulada(st.session_state.df_riesgos), use_container_width=True)

# ---- MONTE CARLO ----
st.subheader("Simulación Monte Carlo")
col1, col2 = st.columns(2)
with col1:
    min_prob = st.slider("Probabilidad mínima", 1, 100, 10)
    max_prob = st.slider("Probabilidad máxima", min_prob, 100, 80)
    min_imp = st.slider("Impacto mínimo", 1, 100, 20)
    max_imp = st.slider("Impacto máximo", min_imp, 100, 90)
with col2:
    n_iter = st.number_input("Iteraciones", min_value=100, max_value=100000, value=1000)

riesgos_simulados = simular_montecarlo(n_iter, min_prob, max_prob, min_imp, max_imp)
stats = generar_estadisticas_montecarlo(riesgos_simulados)

st.plotly_chart(generar_histograma(riesgos_simulados), use_container_width=True)

st.markdown(f"<div class='metric-box'><h3>{textos['media']}: {stats['media']:.2f}</h3></div>", unsafe_allow_html=True)
st.markdown(f"<div class='metric-box'><h3>{textos['max']}: {stats['max']:.2f}</h3></div>", unsafe_allow_html=True)
st.markdown(f"<div class='metric-box'><h3>{textos['min']}: {stats['min']:.2f}</h3></div>", unsafe_allow_html=True)
st.markdown(f"<div class='metric-box'><h3>{textos['percentil_95']}: {stats['percentil_95']:.2f}</h3></div>", unsafe_allow_html=True)
