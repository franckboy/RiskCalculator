import streamlit as st
import pandas as pd
import numpy as np
from data_config import (
    tabla_tipo_impacto, matriz_probabilidad, matriz_impacto,
    factor_exposicion, factor_probabilidad, efectividad_controles,
    criticidad_límites, textos
)
from calculations import (
    clasificar_criticidad, calcular_criticidad, simular_montecarlo
)
from plotting import (
    create_heatmap, create_pareto_chart,
    plot_montecarlo_histogram, create_sensitivity_plot
)
from utils import reset_form_fields, format_risk_dataframe

# --- Configuración de la página ---
st.set_page_config(
    layout="wide",
    page_title="Calculadora de Riesgos",
    page_icon="🛡️"
)

# --- CSS Personalizado ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# --- Inicialización de Session State ---
if 'idioma' not in st.session_state:
    st.session_state.idioma = 'es'
if 'riesgos' not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "ID", "Nombre del Riesgo", "Descripción", "Tipo de Impacto",
        "Probabilidad", "Exposición", "Impacto Numérico",
        "Efectividad del Control (%)", "Amenaza Deliberada",
        "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación", "Color"
    ])
if 'current_edit_index' not in st.session_state:
    st.session_state.current_edit_index = -1  # -1 = no edición

# --- Funciones de ayuda ---
def get_text(key):
    """Obtiene texto traducido según el idioma."""
    return textos[st.session_state.idioma].get(key, key)

# --- Sidebar ---
with st.sidebar:
    # Selector de idioma
    if st.checkbox(
        get_text("sidebar_language_toggle"),
        value=(st.session_state.idioma == 'en')
    ):
        st.session_state.idioma = 'en'
    else:
        st.session_state.idioma = 'es'

    st.markdown("---")
    st.header(get_text("tax_info_title"))
    st.info(get_text("tax_info_text"))

# --- Título principal ---
st.title(get_text("app_title"))
st.markdown("---")

# --- Columnas principales ---
col_form, col_graf = st.columns([1, 1.5])

# --- Columna 1: Formulario y resultados deterministas ---
with col_form:
    st.header(get_text("risk_input_form_title"))

    with st.form("risk_form", clear_on_submit=False):
        # Campos del formulario
        risk_name = st.text_input(
            get_text("risk_name"),
            key="risk_name_input"
        )
        risk_description = st.text_area(
            get_text("risk_description"),
            key="risk_description_input"
        )
        
        selected_type_impact = st.selectbox(
            get_text("risk_type_impact"),
            tabla_tipo_impacto['Tipo de Impacto'],
            key="selected_type_impact"
        )
        
        selected_probabilidad = st.selectbox(
            get_text("risk_probability"),
            factor_probabilidad['Clasificacion'],
            key="selected_probabilidad"
        )
        
        selected_exposicion = st.selectbox(
            get_text("risk_exposure"),
            factor_exposicion['Clasificacion'],
            key="selected_exposicion"
        )
        
        impacto_numerico = st.slider(
            get_text("risk_impact_numeric"),
            min_value=0, max_value=100, value=50,
            key="impacto_numerico_slider"
        )
        
        efectividad_control = st.slider(
            get_text("risk_control_effectiveness"),
            min_value=0, max_value=100, value=50,
            key="control_effectiveness_slider"
        )
        
        amenaza_deliberada = st.checkbox(
            get_text("risk_deliberate_threat"),
            key="deliberate_threat_checkbox"
        )
        
        submitted = st.form_submit_button(get_text("add_risk_button"))

    # --- Resultados deterministas ---
    if submitted and risk_name:
        # Cálculos (usando funciones de calculations.py)
        prob_factor = factor_probabilidad.loc[
            factor_probabilidad['Clasificacion'] == selected_probabilidad,
            'Factor'
        ].iloc[0]
        
        expo_factor = factor_exposicion.loc[
            factor_exposicion['Clasificacion'] == selected_exposicion,
            'Factor'
        ].iloc[0]
        
        amenaza_deliberada_factor = 1 if amenaza_deliberada else 0
        ponderacion_impacto = tabla_tipo_impacto.loc[
            tabla_tipo_impacto['Tipo de Impacto'] == selected_type_impact,
            'Ponderación'
        ].iloc[0]
        
        # Calcular métricas
        amenaza_inherente, amenaza_residual, amenaza_ajustada, riesgo_residual = calcular_criticidad(
            prob_factor, expo_factor, amenaza_deliberada_factor,
            efectividad_control, impacto_numerico, ponderacion_impacto
        )
        
        clasificacion, color = clasificar_criticidad(riesgo_residual, st.session_state.idioma)
        
        # Guardar en session_state
        nuevo_riesgo = {
            "ID": len(st.session_state.riesgos) + 1,
            "Nombre del Riesgo": risk_name,
            "Descripción": risk_description,
            "Tipo de Impacto": selected_type_impact,
            "Probabilidad": prob_factor,
            "Exposición": expo_factor,
            "Impacto Numérico": impacto_numerico,
            "Efectividad del Control (%)": efectividad_control,
            "Amenaza Deliberada": "Sí" if amenaza_deliberada else "No",
            "Amenaza Inherente": f"{amenaza_inherente:.2f}",
            "Amenaza Residual": f"{amenaza_residual:.2f}",
            "Amenaza Residual Ajustada": f"{amenaza_ajustada:.2f}",
            "Riesgo Residual": riesgo_residual,
            "Clasificación": clasificacion,
            "Color": color
        }
        
        st.session_state.riesgos = pd.concat([
            st.session_state.riesgos,
            pd.DataFrame([nuevo_riesgo])
        ], ignore_index=True)
        
        st.success(get_text("success_risk_added"))
        reset_form_fields()

# --- Columna 2: Visualizaciones ---
with col_graf:
    # Mapa de calor
    st.header(get_text("risk_heatmap_title"))
    if not st.session_state.riesgos.empty:
        fig_heatmap = create_heatmap(
            st.session_state.riesgos,
            matriz_probabilidad,
            matriz_impacto,
            st.session_state.idioma
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info(get_text("no_risks_yet"))

    # Gráfico de Pareto
    st.header(get_text("risk_pareto_chart_title"))
    if not st.session_state.riesgos.empty:
        fig_pareto = create_pareto_chart(
            st.session_state.riesgos,
            st.session_state.idioma
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

# --- Ejecutar la app ---
if __name__ == "__main__":
    st.rerun()
