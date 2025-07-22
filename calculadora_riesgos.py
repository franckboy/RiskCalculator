import streamlit as st
import pandas as pd
import numpy as np
from data_config import tabla_tipo_impacto, factor_exposicion, factor_probabilidad, textos
from calculations import clasificar_criticidad, calcular_criticidad, simular_montecarlo
from plotting import create_heatmap, create_pareto_chart, plot_montecarlo_histogram, create_sensitivity_plot
from utils import format_risk_dataframe, reset_form_fields

# --- Configuración de la página ---
st.set_page_config(layout="wide", page_title="Calculadora de Riesgos", page_icon="🛡️")

# --- CSS Personalizado ---
st.markdown("""
<style>
.stButton>button {background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 8px;}
</style>""", unsafe_allow_html=True)

# --- Inicialización de Session State ---
if 'idioma' not in st.session_state: st.session_state.idioma = 'es'
if 'current_edit_id' not in st.session_state: st.session_state.current_edit_id = None
if 'riesgos' not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "ID", "Nombre del Riesgo", "Descripción", "Tipo de Impacto", "Probabilidad", 
        "Probabilidad Texto", "Exposición", "Exposición Texto", "Impacto Numérico", 
        "Efectividad del Control (%)", "Amenaza Deliberada", "Amenaza Inherente", 
        "Amenaza Residual", "Amenaza Residual Ajustada", "Riesgo Residual", 
        "Clasificación", "Color"
    ])

# --- Funciones de ayuda ---
def get_text(key): return textos.get(st.session_state.idioma, {}).get(key, key)

# --- Sidebar ---
with st.sidebar:
    lang_value = st.session_state.idioma == 'en'
    if st.checkbox(get_text("sidebar_language_toggle"), value=lang_value):
        st.session_state.idioma = 'en'
    else:
        st.session_state.idioma = 'es'
    st.markdown("---")
    st.header(get_text("tax_info_title"))
    st.info(get_text("tax_info_text"))

# --- Título ---
st.title(get_text("app_title"))
st.markdown("---")

# --- Layout Principal ---
col_form, col_graf = st.columns([1, 1.5], gap="large")

# --- Columna 1: Formulario y Tabla de Riesgos ---
with col_form:
    st.header(get_text("risk_input_form_title"))
    
    if st.session_state.current_edit_id:
        st.info(f"{get_text('editing_risk')}: **{st.session_state.riesgos.loc[st.session_state.riesgos['ID'] == st.session_state.current_edit_id, 'Nombre del Riesgo'].item()}**")
        if st.button(f"➕ {get_text('create_new_risk_button')}", type="secondary"):
            st.session_state.current_edit_id = None
            reset_form_fields()
            st.rerun()

    with st.form("risk_form", clear_on_submit=(st.session_state.current_edit_id is None)):
        risk_name = st.text_input(get_text("risk_name"), key="risk_name_input")
        # Resto de los campos del formulario
        risk_description = st.text_area(get_text("risk_description"), key="risk_description_input")
        selected_type_impact = st.selectbox(get_text("risk_type_impact"), tabla_tipo_impacto['Tipo de Impacto'], key="selected_type_impact")
        selected_probabilidad = st.selectbox(get_text("risk_probability"), factor_probabilidad['Clasificacion'], key="selected_probabilidad")
        selected_exposicion = st.selectbox(get_text("risk_exposure"), factor_exposicion['Clasificacion'], key="selected_exposicion")
        impacto_numerico = st.slider(get_text("risk_impact_numeric"), 0, 100, 50, key="impacto_numerico_slider")
        efectividad_control = st.slider(get_text("risk_control_effectiveness"), 0, 100, 50, key="control_effectiveness_slider")
        amenaza_deliberada = st.checkbox(get_text("risk_deliberate_threat"), key="deliberate_threat_checkbox")
        
        submit_label = get_text("update_risk_button") if st.session_state.current_edit_id else get_text("add_risk_button")
        submitted = st.form_submit_button(submit_label)

    if submitted and risk_name:
        prob_factor = factor_probabilidad.loc[factor_probabilidad['Clasificacion'] == selected_probabilidad, 'Factor'].item()
        expo_factor = factor_exposicion.loc[factor_exposicion['Clasificacion'] == selected_exposicion, 'Factor'].item()
        amenaza_deliberada_factor = 1 if amenaza_deliberada else 0
        ponderacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto['Tipo de Impacto'] == selected_type_impact, 'Ponderación'].item()

        amenaza_inherente, amenaza_residual, amenaza_ajustada, riesgo_residual = calcular_criticidad(prob_factor, expo_factor, amenaza_deliberada_factor, efectividad_control, impacto_numerico, ponderacion_impacto)
        clasificacion, color = clasificar_criticidad(riesgo_residual, st.session_state.idioma)

        risk_data = {"Nombre del Riesgo": risk_name, "Descripción": risk_description, "Tipo de Impacto": selected_type_impact, "Probabilidad": prob_factor, "Probabilidad Texto": selected_probabilidad, "Exposición": expo_factor, "Exposición Texto": selected_exposicion, "Impacto Numérico": impacto_numerico, "Efectividad del Control (%)": efectividad_control, "Amenaza Deliberada": "Sí" if amenaza_deliberada else "No", "Amenaza Inherente": f"{amenaza_inherente:.3f}", "Amenaza Residual": f"{amenaza_residual:.3f}", "Amenaza Residual Ajustada": f"{amenaza_ajustada:.3f}", "Riesgo Residual": riesgo_residual, "Clasificación": clasificacion, "Color": color}

        if st.session_state.current_edit_id:
            idx = st.session_state.riesgos.index[st.session_state.riesgos["ID"] == st.session_state.current_edit_id].item()
            for key, value in risk_data.items(): st.session_state.riesgos.loc[idx, key] = value
            st.success(get_text("success_risk_updated"))
            st.session_state.current_edit_id = None
            reset_form_fields()
            st.rerun()
        else:
            new_id = (st.session_state.riesgos['ID'].max() + 1) if not st.session_state.riesgos.empty else 1
            risk_data["ID"] = new_id
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([risk_data])], ignore_index=True)
            st.success(get_text("success_risk_added"))

    st.markdown("---")
    st.header(get_text("risk_table_title"))
    if not st.session_state.riesgos.empty:
        df_display = st.session_state.riesgos[['ID', 'Nombre del Riesgo', 'Riesgo Residual', 'Clasificación']].copy()
        for r_id, r_name in df_display[['ID', 'Nombre del Riesgo']].values:
            if st.button(f"✏️ {r_name}", key=f"edit_{r_id}", use_container_width=True):
                st.session_state.current_edit_id = r_id
                risk_to_load = st.session_state.riesgos.loc[st.session_state.riesgos['ID'] == r_id].iloc[0]
                # Poblar el formulario
                st.session_state.risk_name_input = risk_to_load["Nombre del Riesgo"]
                st.session_state.risk_description_input = risk_to_load["Descripción"]
                st.session_state.selected_type_impact = risk_to_load["Tipo de Impacto"]
                st.session_state.selected_probabilidad = risk_to_load["Probabilidad Texto"]
                st.session_state.selected_exposicion = risk_to_load["Exposición Texto"]
                st.session_state.impacto_numerico_slider = int(risk_to_load["Impacto Numérico"])
                st.session_state.control_effectiveness_slider = int(risk_to_load["Efectividad del Control (%)"])
                st.session_state.deliberate_threat_checkbox = (risk_to_load["Amenaza Deliberada"] == "Sí")
                st.rerun()
        st.dataframe(format_risk_dataframe(df_display.rename(columns={'Riesgo Residual': 'Valor del Riesgo'})), use_container_width=True, hide_index=True)
    else: st.info(get_text("no_risks_yet"))

# --- Columna 2: Visualizaciones ---
with col_graf:
    st.header(get_text("risk_analysis_title"))
    if not st.session_state.riesgos.empty:
        tab1, tab2 = st.tabs(["🔥 Mapa de Calor", "📊 Pareto"])
        with tab1: st.plotly_chart(create_heatmap(st.session_state.riesgos, st.session_state.idioma), use_container_width=True)
        with tab2: st.plotly_chart(create_pareto_chart(st.session_state.riesgos, st.session_state.idioma), use_container_width=True)
    else: st.info(get_text("no_risks_yet"))
    
    st.markdown("---")
    st.header(f"🎲 {get_text('montecarlo_title')}")
    if not st.session_state.riesgos.empty:
        options = st.session_state.riesgos.set_index('ID')['Nombre del Riesgo']
        risk_id = st.selectbox("Selecciona un riesgo para simular", options.index, format_func=lambda id: options[id], key="mc_risk_select")
        
        if risk_id:
            valor_economico = st.number_input(get_text("economic_value_input"), min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
            num_iter = st.select_slider(get_text("montecarlo_iterations"), options=[1000, 5000, 10000, 20000, 50000], value=10000)

            if st.button(f"▶️ {get_text('run_simulation_button')}"):
                with st.spinner("Ejecutando simulación..."):
                    risk = st.session_state.riesgos.loc[st.session_state.riesgos['ID'] == risk_id].iloc[0]
                    ponderacion = tabla_tipo_impacto.loc[tabla_tipo_impacto['Tipo de Impacto'] == risk['Tipo de Impacto'], 'Ponderación'].item()
                    
                    riesgo_sim, perdida_sim, correlations = simular_montecarlo(
                        probabilidad_base=risk['Probabilidad'], exposicion_base=risk['Exposición'],
                        impacto_numerico_base=risk['Impacto Numérico'], efectividad_base_pct=risk['Efectividad del Control (%)'],
                        amenaza_deliberada_factor_base=1 if risk['Amenaza Deliberada'] == 'Sí' else 0,
                        ponderacion_impacto=ponderacion, valor_economico=valor_economico, iteraciones=num_iter
                    )

                if perdida_sim is not None and len(perdida_sim) > 0:
                    st.subheader(get_text("simulation_results_title"))
                    c1, c2, c3 = st.columns(3)
                    c1.metric(get_text("avg_loss_metric"), f"${perdida_sim.mean():,.2f}")
                    c2.metric(get_text("max_loss_metric"), f"${perdida_sim.max():,.2f}")
                    c3.metric(get_text("var_95_metric"), f"${np.percentile(perdida_sim, 95):,.2f}")
                    
                    st.plotly_chart(plot_montecarlo_histogram(perdida_sim, st.session_state.idioma), use_container_width=True)
                    st.plotly_chart(create_sensitivity_plot(correlations, st.session_state.idioma), use_container_width=True)
                else:
                    st.error("La simulación no pudo completarse. Asegúrate que el valor económico sea mayor a cero.")
    else: st.info(get_text("no_risks_yet"))
