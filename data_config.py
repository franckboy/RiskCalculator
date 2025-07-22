import pandas as pd
# Tablas base para el modelo de riesgo
tabla_tipo_impacto = pd.DataFrame({
    'Tipo de Impacto': ['Humano', 'Operacional', 'Económico', 'Reputacional', 'Legal'],
    'Ponderación': [25, 20, 30, 15, 10]
})

matriz_probabilidad = pd.DataFrame({
    'Clasificacion': ['Muy Baja', 'Baja', 'Media', 'Alta', 'Muy Alta'],
    'Valor': [0.1, 0.3, 0.5, 0.7, 0.9]
})

matriz_impacto = pd.DataFrame({
    'Clasificacion': ['Insignificante', 'Menor', 'Moderado', 'Mayor', 'Catastrófico'],
    'Valor': [1, 2, 3, 4, 5]
})

factor_exposicion = pd.DataFrame({
    'Clasificacion': ['Baja', 'Media', 'Alta'],
    'Factor': [0.3, 0.6, 0.9]
})

factor_probabilidad = pd.DataFrame({
    'Clasificacion': ['Baja', 'Media', 'Alta'],
    'Factor': [0.3, 0.6, 0.9]
})

efectividad_controles = pd.DataFrame({
    'Efectividad': ['Inefectiva', 'Parcialmente Efectiva', 'Efectiva', 'Muy Efectiva'],
    'Rango % Min': [0, 26, 51, 76],
    'Rango % Max': [25, 50, 75, 100]
})

criticidad_límites = [
    (0.0, 0.1, 'ACEPTABLE', '#28a745', 'ACCEPTABLE'),
    (0.1, 0.2, 'TOLERABLE', '#90EE90', 'TOLERABLE'),
    (0.2, 0.4, 'MODERADO', '#ffc107', 'MODERATE'),
    (0.4, 0.6, 'ALTO', '#fd7e14', 'HIGH'),
    (0.6, 1.0, 'CRÍTICO', '#dc3545', 'CRITICAL')
]

# Textos para internacionalización (i18n)
textos = {
    "es": {
        "app_title": "Calculadora de Riesgos y Simulador Monte Carlo",
        "sidebar_language_toggle": "Switch to English",
        "tax_info_title": "Taxonomía de Riesgo",
        "tax_info_text": "Este modelo se basa en una taxonomía estándar de riesgos de seguridad.",
        "risk_input_form_title": "Registro y Edición de Riesgos",
        "select_risk_to_edit": "Selecciona un riesgo para editar o visualizar",
        "editing_risk": "📝 Editando Riesgo Existente",
        "adding_new_risk": "➕ Agregando Nuevo Riesgo",
        "create_new_risk_button": "Crear Nuevo Riesgo",
        "risk_name": "Nombre del Riesgo",
        "risk_description": "Descripción del Riesgo",
        "risk_type_impact": "Tipo de Impacto Principal",
        "risk_probability": "Probabilidad de Amenaza",
        "risk_exposure": "Frecuencia de Exposición",
        "risk_impact_numeric": "Valor del Impacto (0-100)",
        "risk_control_effectiveness": "Efectividad del Control (%)",
        "risk_deliberate_threat": "Es una Amenaza Deliberada",
        "add_risk_button": "✔️ Agregar Riesgo",
        "update_risk_button": "✔️ Actualizar Riesgo",
        "success_risk_added": "Riesgo agregado exitosamente.",
        "success_risk_updated": "Riesgo actualizado exitosamente.",
        "risk_table_title": "Tabla de Riesgos Registrados",
        "risk_analysis_title": "Análisis de Riesgos",
        "no_risks_yet": "Aún no hay riesgos registrados.",
        "risk_heatmap_title": "Mapa de Calor de Riesgos",
        "risk_pareto_chart_title": "Análisis de Pareto",
        "montecarlo_title": "Simulación Monte Carlo",
        "economic_value_input": "Valor económico del activo (USD)",
        "montecarlo_iterations": "Número de Iteraciones",
        "run_simulation_button": "Ejecutar Simulación",
        "simulation_results_title": "Resultados de la Simulación",
        "avg_loss_metric": "Pérdida Promedio",
        "max_loss_metric": "Pérdida Máxima",
        "var_95_metric": "Pérdida al 95% (VaR)",
        "sensitivity_analysis_title": "Análisis de Sensibilidad",
        "loss_distribution_title": "Distribución de Pérdidas Potenciales"
    },
    "en": {
        "app_title": "Risk Calculator and Monte Carlo Simulator",
        "sidebar_language_toggle": "Cambiar a Español",
        "tax_info_title": "Risk Taxonomy",
        "tax_info_text": "This model is based on a standard security risk taxonomy.",
        "risk_input_form_title": "Risk Registry and Editor",
        "select_risk_to_edit": "Select a risk to edit or view",
        "editing_risk": "📝 Editing Existing Risk",
        "adding_new_risk": "➕ Adding New Risk",
        "create_new_risk_button": "Create New Risk",
        "risk_name": "Risk Name",
        "risk_description": "Risk Description",
        "risk_type_impact": "Main Impact Type",
        "risk_probability": "Threat Probability",
        "risk_exposure": "Exposure Frequency",
        "risk_impact_numeric": "Impact Value (0-100)",
        "risk_control_effectiveness": "Control Effectiveness (%)",
        "risk_deliberate_threat": "Is a Deliberate Threat",
        "add_risk_button": "✔️ Add Risk",
        "update_risk_button": "✔️ Update Risk",
        "success_risk_added": "Risk added successfully.",
        "success_risk_updated": "Risk updated successfully.",
        "risk_table_title": "Registered Risks Table",
        "risk_analysis_title": "Risk Analysis",
        "no_risks_yet": "No risks registered yet.",
        "risk_heatmap_title": "Risk Heatmap",
        "risk_pareto_chart_title": "Pareto Analysis",
        "montecarlo_title": "Monte Carlo Simulation",
        "economic_value_input": "Economic value of the asset (USD)",
        "montecarlo_iterations": "Number of Iterations",
        "run_simulation_button": "Run Simulation",
        "simulation_results_title": "Simulation Results",
        "avg_loss_metric": "Average Loss",
        "max_loss_metric": "Maximum Loss",
        "var_95_metric": "95th Percentile Loss (VaR)",
        "sensitivity_analysis_title": "Sensitivity Analysis",
        "loss_distribution_title": "Potential Loss Distribution"
    }
}
