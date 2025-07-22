import streamlit as st
from data_config import criticidad_límites

def format_risk_dataframe(df_risks):
    """Aplica formato de color a la columna de valor de riesgo."""
    if df_risks.empty:
        return df_risks

    def get_color(val):
        try:
            val = float(val)
        except (ValueError, TypeError):
            return ''
            
        for v_min, v_max, _, color, _ in criticidad_límites:
            if (v_min < val <= v_max) or (val == 0.0 and v_min == 0.0):
                return f'background-color: {color}; color: black;'
        return ''

    # Aplica el estilo solo a la columna 'Valor del Riesgo'
    return df_risks.style.apply(
        lambda s: [get_color(v) for v in s],
        subset=['Valor del Riesgo']
    ).format({'Valor del Riesgo': "{:.3f}"})

def reset_form_fields():
    """Limpia los campos del formulario en el session_state."""
    st.session_state.risk_name_input = ""
    st.session_state.risk_description_input = ""
    st.session_state.impacto_numerico_slider = 50
    st.session_state.control_effectiveness_slider = 50
    st.session_state.deliberate_threat_checkbox = False
    # Reinicia los selectores a su primera opción si es necesario
    if 'selected_type_impact' in st.session_state:
        del st.session_state['selected_type_impact']
    if 'selected_probabilidad' in st.session_state:
        del st.session_state['selected_probabilidad']
    if 'selected_exposicion' in st.session_state:
        del st.session_state['selected_exposicion']
