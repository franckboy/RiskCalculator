import streamlit as st
import pandas as pd
from data_config import criticidad_límites

def reset_form_fields():
    """Reinicia los campos del formulario de entrada de riesgo."""
    st.session_state['risk_name_input'] = ""
    st.session_state['risk_description_input'] = ""
    st.session_state['selected_type_impact'] = st.session_state['default_type_impact']
    st.session_state['selected_probabilidad'] = st.session_state['default_probabilidad']
    st.session_state['selected_exposicion'] = st.session_state['default_exposicion']
    st.session_state['impacto_numerico_slider'] = st.session_state['default_impacto_numerico']
    st.session_state['control_effectiveness_slider'] = st.session_state['default_control_effectiveness']
    st.session_state['deliberate_threat_checkbox'] = False
    st.session_state['current_edit_index'] = -1 # Asegurarse de que no estamos en modo edición


def format_risk_dataframe(df_risks, idioma="es"):
    """
    Formatea el DataFrame de riesgos para una mejor visualización en Streamlit,
    aplicando colores de criticidad.
    """
    if df_risks.empty:
        return df_risks

    def get_color(val):
        for v_min, v_max, _, color, _ in criticidad_límites:
            if v_min <= val <= v_max:
                return f'background-color: {color};'
        return ''

    styled_df = df_risks.style.applymap(get_color, subset=['Riesgo Residual'])

    return styled_df
