import streamlit as st
import pandas as pd
from data_config import criticidad_límites

def reset_form_fields():
    st.session_state['risk_name_input'] = ""
    st.session_state['risk_description_input'] = ""
    st.session_state['selected_type_impact'] = st.session_state.get('default_type_impact')
    st.session_state['selected_probabilidad'] = st.session_state.get('default_probabilidad')
    st.session_state['selected_exposicion'] = st.session_state.get('default_exposicion')
    st.session_state['impacto_numerico_slider'] = st.session_state.get('default_impacto_numerico')
    st.session_state['control_effectiveness_slider'] = st.session_state.get('default_control_effectiveness')
    st.session_state['deliberate_threat_checkbox'] = False
    st.session_state['current_edit_index'] = -1

def format_risk_dataframe(df_risks, idioma="es"):
    if df_risks.empty:
        return df_risks

    def get_color(val):
        for v_min, v_max, _, color, _ in criticidad_límites:
            if v_min <= val <= v_max:
                return f'background-color: {color};'
        return ''

    return df_risks.style.applymap(get_color, subset=['Riesgo Residual'])
