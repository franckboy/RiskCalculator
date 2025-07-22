import pandas as pd
import numpy as np

# Tablas base para el modelo de riesgo
tabla_tipo_impacto = pd.DataFrame({
    'Tipo de Impacto': ['Humano', 'Operacional', 'Económico', 'Reputacional', 'Legal'],
    'Ponderación': [25, 20, 30, 15, 10], # Suma 100
    'Explicación ASIS': [
        'Afectación a la vida, salud o seguridad de personas.',
        'Interrupción o degradación de procesos y funciones del negocio.',
        'Pérdidas financieras directas o indirectas.',
        'Daño a la imagen, confianza o credibilidad de la organización.',
        'Incumplimiento de leyes, regulaciones o contratos.'
    ]
})

matriz_probabilidad = pd.DataFrame({
    'Clasificacion': ['Muy Baja', 'Baja', 'Media', 'Alta', 'Muy Alta'],
    'Valor': [0.1, 0.3, 0.5, 0.7, 0.9],
    'Definición': [
        'Probabilidad de ocurrencia menor al 10%',
        'Probabilidad de ocurrencia entre 10% y 30%',
        'Probabilidad de ocurrencia entre 30% y 50%',
        'Probabilidad de ocurrencia entre 50% y 70%',
        'Probabilidad de ocurrencia mayor al 70%'
    ]
})

matriz_impacto = pd.DataFrame({
    'Clasificacion': ['Insignificante', 'Menor', 'Moderado', 'Mayor', 'Catastrófico'],
    'Valor': [1, 2, 3, 4, 5], # Para mapeo interno si es necesario, aunque el slider es el principal
    'Definición': [
        'Daño mínimo, fácilmente recuperable.',
        'Daño localizado, impacto limitado.',
        'Daño significativo, impacto moderado en áreas clave.',
        'Daño extenso, impacto severo en la operación.',
        'Daño crítico, amenaza la viabilidad de la organización.'
    ]
})

factor_exposicion = pd.DataFrame({
    'Clasificacion': ['Baja', 'Media', 'Alta'],
    'Factor': [0.3, 0.6, 0.9],
    'Definición': [
        'Contacto con la amenaza es ocasional o nulo.',
        'Contacto con la amenaza es frecuente o regular.',
        'Contacto con la amenaza es constante o inevitable.'
    ]
})

factor_probabilidad = pd.DataFrame({
    'Clasificacion': ['Baja', 'Media', 'Alta'],
    'Factor': [0.3, 0.6, 0.9],
    'Definición': [
        'La probabilidad de que una amenaza se materialice es baja.',
        'La probabilidad de que una amenaza se materialice es media.',
        'La probabilidad de que una amenaza se materialice es alta.'
    ]
})

efectividad_controles = pd.DataFrame({
    'Efectividad': ['Inefectiva', 'Parcialmente Efectiva', 'Efectiva', 'Muy Efectiva'],
    'Rango % Min': [0, 26, 51, 76],
    'Rango % Max': [25, 50, 75, 100],
    'Factor': [0.1, 0.3, 0.7, 0.9], # Factor para reducir el riesgo
    'Mitigacion': [
        'Los controles no reducen significativamente el riesgo.',
        'Los controles ofrecen una reducción limitada del riesgo.',
        'Los controles reducen el riesgo de manera considerable.',
        'Los controles casi eliminan el riesgo.'
    ]
})

criticidad_límites = [
    (0, 0.1, 'ACEPTABLE', '#28a745', 'ACCEPTABLE'), # Verde
    (0.1, 0.2, 'TOLERABLE', '#90EE90', 'TOLERABLE'), # Verde Claro
    (0.2, 0.4, 'MODERADO', '#ffc107', 'MODERATE'), # Amarillo
    (0.4, 0.6, 'ALTO', '#fd7e14', 'HIGH'), # Naranja
    (0.6, 1.0, 'CRÍTICO', '#dc3545', 'CRITICAL')  # Rojo
]

# Diccionario para manejo de múltiples idiomas
textos = {
    "es": {
        "sidebar_language_toggle": "English",
        "app_title": "Calculadora de Riesgos y Simulador Monte Carlo",
        "tax_info_title": "Consideraciones sobre Impuestos",
        "tax_info_text": "Las implicaciones fiscales de las pérdidas por riesgos pueden ser complejas y varían significativamente según la jurisdicción y el tipo de negocio. Esta sección proporciona información general. Es crucial consultar a un asesor fiscal profesional para comprender cómo las pérdidas relacionadas con riesgos podrían afectar su situación fiscal específica, incluyendo posibles deducciones, créditos o tratamientos contables. Factores como la naturaleza de la pérdida (ej. operativa vs. capital), la estructura legal de la entidad y las leyes fiscales locales e internacionales son determinantes. Este simulador no ofrece asesoramiento fiscal.",
        "risk_input_form_title": "1. Entrada de Datos del Riesgo",
        "risk_name": "Nombre del Riesgo",
        "risk_description": "Descripción Detallada del Riesgo",
        "risk_type_impact": "Tipo de Impacto Principal",
        "risk_probability": "Probabilidad de Ocurrencia (Amenaza Inherente)",
        "risk_exposure": "Exposición (Amenaza Inherente)",
        "risk_impact_numeric": "Impacto Numérico (0-100)",
        "risk_control_effectiveness": "Efectividad del Control (%)",
        "risk_deliberate_threat": "¿Amenaza Deliberada?",
        "add_risk_button": "Agregar Riesgo",
        "error_risk_name_empty": "Por favor, ingresa un nombre para el riesgo.",
        "success_risk_added": "Riesgo agregado exitosamente.",
        "deterministic_results_title": "2. Resultados del Modelo Determinista",
        "inherent_threat": "Amenaza Inherente",
        "residual_threat": "Amenaza Residual",
        "adjusted_residual_threat": "Amenaza Residual Ajustada",
        "residual_risk": "Riesgo Residual",
        "classification": "Clasificación",
        "montecarlo_input_title": "3. Configuración de Simulación Monte Carlo",
        "economic_value_asset": "Valor Económico del Activo Bajo Riesgo (USD)",
        "num_iterations": "Número de Iteraciones Monte Carlo",
        "run_montecarlo_button": "Lanzar Simulación Monte Carlo",
        "montecarlo_results_title": "4. Resultados de la Simulación Monte Carlo",
        "expected_loss": "Pérdida Esperada (Media)",
        "median_loss": "Pérdida Mediana (Percentil 50)",
        "p5_loss": "Pérdida del Percentil 5",
        "p90_loss": "Pérdida del Percentil 90",
        "max_loss": "Máxima Pérdida Simulada",
        "cvar_95": "CVaR (95% - Cola de Riesgo)",
        "sensitivity_analysis_title": "Análisis de Sensibilidad (Correlación con Pérdida Económica)",
        "added_risks_title": "5. Riesgos Evaluados Acumulados",
        "download_excel_button": "Descargar Datos a Excel",
        "no_risks_yet": "Aún no se han agregado riesgos.",
        "risk_heatmap_title": "6. Mapa de Calor de Riesgos (Modelo Determinista)",
        "risk_pareto_chart_title": "7. Gráfico de Pareto de Riesgos",
        "risk_distribution_title": "8. Distribución del Riesgo Residual Simulado (Índice)",
        "economic_loss_distribution_title": "9. Distribución de Pérdidas Económicas Simuladas (USD)",
        "edit_risk": "Editar",
        "delete_risk": "Eliminar",
        "confirm_delete": "¿Estás seguro de que quieres eliminar este riesgo?",
        "risk_deleted": "Riesgo eliminado exitosamente."

    },
    "en": {
        "sidebar_language_toggle": "Español",
        "app_title": "Risk Calculator and Monte Carlo Simulator",
        "tax_info_title": "Tax Considerations",
        "tax_info_text": "The tax implications of risk losses can be complex and vary significantly by jurisdiction and business type. This section provides general information. It is crucial to consult a professional tax advisor to understand how risk-related losses might affect your specific tax situation, including potential deductions, credits, or accounting treatments. Factors such as the nature of the loss (e.g., operational vs. capital), the legal structure of the entity, and local and international tax laws are determining factors. This simulator does not provide tax advice.",
        "risk_input_form_title": "1. Risk Data Input",
        "risk_name": "Risk Name",
        "risk_description": "Detailed Risk Description",
        "risk_type_impact": "Primary Impact Type",
        "risk_probability": "Probability of Occurrence (Inherent Threat)",
        "risk_exposure": "Exposure (Inherent Threat)",
        "risk_impact_numeric": "Numeric Impact (0-100)",
        "risk_control_effectiveness": "Control Effectiveness (%)",
        "risk_deliberate_threat": "Deliberate Threat?",
        "add_risk_button": "Add Risk",
        "error_risk_name_empty": "Please enter a name for the risk.",
        "success_risk_added": "Risk added successfully.",
        "deterministic_results_title": "2. Deterministic Model Results",
        "inherent_threat": "Inherent Threat",
        "residual_threat": "Residual Threat",
        "adjusted_residual_threat": "Adjusted Residual Threat",
        "residual_risk": "Residual Risk",
        "classification": "Classification",
        "montecarlo_input_title": "3. Monte Carlo Simulation Setup",
        "economic_value_asset": "Economic Value of Asset at Risk (USD)",
        "num_iterations": "Number of Monte Carlo Iterations",
        "run_montecarlo_button": "Run Monte Carlo Simulation",
        "montecarlo_results_title": "4. Monte Carlo Simulation Results",
        "expected_loss": "Expected Loss (Mean)",
        "median_loss": "Median Loss (50th Percentile)",
        "p5_loss": "5th Percentile Loss",
        "p90_loss": "90th Percentile Loss",
        "max_loss": "Maximum Simulated Loss",
        "cvar_95": "CVaR (95% - Tail Risk)",
        "sensitivity_analysis_title": "Sensitivity Analysis (Correlation with Economic Loss)",
        "added_risks_title": "5. Accumulated Evaluated Risks",
        "download_excel_button": "Download Data to Excel",
        "no_risks_yet": "No risks have been added yet.",
        "risk_heatmap_title": "6. Risk Heatmap (Deterministic Model)",
        "risk_pareto_chart_title": "7. Risk Pareto Chart",
        "risk_distribution_title": "8. Simulated Residual Risk Distribution (Index)",
        "economic_loss_distribution_title": "9. Simulated Economic Loss Distribution (USD)",
        "edit_risk": "Edit",
        "delete_risk": "Delete",
        "confirm_delete": "Are you sure you want to delete this risk?",
        "risk_deleted": "Risk deleted successfully."
    }
}


# --- 2. calculations.py ---
# Este módulo contendría las funciones para los cálculos del modelo de riesgo.

def clasificar_criticidad(valor, idioma="es"):
    """
    Clasifica un valor numérico de riesgo en una categoría de criticidad
    y asigna un color asociado.

    Args:
        valor (float): El valor numérico del riesgo residual (0-1).
        idioma (str): El idioma para la clasificación ('es' para español, 'en' para inglés).

    Returns:
        tuple: Una tupla que contiene la clasificación del riesgo y su color asociado.
    """
    for v_min, v_max, clasificacion_es, color, clasificacion_en in criticidad_límites:
        if v_min <= valor <= v_max:
            if idioma == "es":
                return clasificacion_es, color
            else:
                return clasificacion_en, color
    return "DESCONOCIDO", "#cccccc" # Default si no se encuentra en ningún rango

def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada_factor, efectividad, valor_impacto_numerico, ponderacion_impacto):
    """
    Calcula las diferentes métricas de riesgo basadas en un modelo determinista.

    Args:
        probabilidad (float): Factor de probabilidad de ocurrencia (0-1).
        exposicion (float): Factor de exposición (0-1).
        amenaza_deliberada_factor (int): Factor que indica si la amenaza es deliberada (1 si sí, 0 si no).
        efectividad (float): Porcentaje de efectividad del control (0-100).
        valor_impacto_numerico (float): Valor numérico del impacto (0-100).
        ponderacion_impacto (float): Ponderación del tipo de impacto (ej. 25 para humano).

    Returns:
        tuple: Una tupla con (amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual).
    """
    try:
        probabilidad = float(probabilidad)
        exposicion = float(exposicion)
        amenaza_deliberada_factor = float(amenaza_deliberada_factor)
        efectividad = float(efectividad) / 100.0 # Convertir porcentaje a factor (0-1)
        valor_impacto_numerico = float(valor_impacto_numerico)
        ponderacion_impacto = float(ponderacion_impacto)

        impacto_norm = valor_impacto_numerico / 100.0 if valor_impacto_numerico > 0 else 0
        ponderacion_factor = ponderacion_impacto / 100.0

        amenaza_inherente = probabilidad * exposicion
        amenaza_residual = amenaza_inherente * (1 - efectividad)
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor)

        riesgo_residual = amenaza_residual_ajustada * impacto_norm * ponderacion_factor
        riesgo_residual = np.clip(riesgo_residual, 0, 1) # Asegurar que el riesgo residual no exceda 1

        return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

    except Exception as e:
        print(f"Error en calcular_criticidad: {e}")
        return 0.0, 0.0, 0.0, 0.0 # Retornar valores seguros en caso de error

def simular_montecarlo(probabilidad_base, exposicion_base, impacto_numerico_base, efectividad_base_pct, amenaza_deliberada_factor_base, ponderacion_impacto, valor_economico, iteraciones=10000):
    """
    Ejecuta una simulación Monte Carlo para el cálculo de riesgos y pérdidas económicas.

    Args:
        probabilidad_base (float): Factor de probabilidad base.
        exposicion_base (float): Factor de exposición base.
        impacto_numerico_base (float): Valor numérico de impacto base (0-100).
        efectividad_base_pct (float): Porcentaje de efectividad de control base (0-100).
        amenaza_deliberada_factor_base (int): Factor base de amenaza deliberada.
        ponderacion_impacto (float): Ponderación del tipo de impacto.
        valor_economico (float): Valor económico del activo bajo riesgo (USD).
        iteraciones (int): Número de iteraciones para la simulación.

    Returns:
        tuple: Una tupla con (riesgo_residual_sim, perdidas_usd_sim, correlations).
               Retorna arrays vacíos y None si el valor económico es 0 o hay un error.
    """
    if valor_economico <= 0:
        return np.array([]), np.array([]), None

    try:
        efectividad_base = efectividad_base_pct / 100.0
        
        sigma_probabilidad = 0.1
        sigma_exposicion = 0.1
        sigma_impacto_norm = 0.05
        sigma_efectividad = 0.1

        factor_perdida_base = impacto_numerico_base / 100.0
        sigma_factor_perdida = 0.20 * factor_perdida_base
        if sigma_factor_perdida == 0 and factor_perdida_base > 0:
             sigma_factor_perdida = 0.05
        elif factor_perdida_base == 0:
            sigma_factor_perdida = 0

        riesgo_residual_sim = np.zeros(iteraciones)
        perdidas_usd_sim = np.zeros(iteraciones)

        for i in range(iteraciones):
            probabilidad_sim = np.clip(np.random.normal(probabilidad_base, sigma_probabilidad), 0.01, 1.0)
            exposicion_sim = np.clip(np.random.normal(exposicion_base, sigma_exposicion), 0.01, 1.0)
            efectividad_sim = np.clip(np.random.normal(efectividad_base, sigma_efectividad), 0.0, 1.0)
            sim_factor_perdida = np.clip(np.random.normal(factor_perdida_base, sigma_factor_perdida), 0.0, 1.0)
            
            impacto_norm_sim = sim_factor_perdida
            amenaza_deliberada_sim = amenaza_deliberada_factor_base

            amenaza_inherente_sim = probabilidad_sim * exposicion_sim
            amenaza_residual_sim = amenaza_inherente_sim * (1 - efectividad_sim)
            amenaza_residual_ajustada_sim = amenaza_residual_sim * (1 + amenaza_deliberada_sim)
            
            riesgo_residual_iter = amenaza_residual_ajustada_sim * impacto_norm_sim * (ponderacion_impacto / 100.0)
            riesgo_residual_sim[i] = np.clip(riesgo_residual_iter, 0, 1)
            perdidas_usd_sim[i] = riesgo_residual_sim[i] * valor_economico

        df_sim = pd.DataFrame({
            'probabilidad': np.array([np.random.normal(probabilidad_base, sigma_probabilidad) for _ in range(iteraciones)]),
            'exposicion': np.array([np.random.normal(exposicion_base, sigma_exposicion) for _ in range(iteraciones)]),
            'impacto_norm': np.array([np.random.normal(factor_perdida_base, sigma_factor_perdida) for _ in range(iteraciones)]),
            'efectividad': np.array([np.random.normal(efectividad_base, sigma_efectividad) for _ in range(iteraciones)]),
            'perdida_usd': perdidas_usd_sim
        })
        
        valid_cols = [col for col in ['probabilidad', 'exposicion', 'impacto_norm', 'efectividad'] if df_sim[col].std() > 0]
        
        if valid_cols:
            correlations = df_sim[valid_cols + ['perdida_usd']].corr(method='pearson')['perdida_usd'].drop('perdida_usd').abs().sort_values(ascending=False)
        else:
            correlations = pd.Series(dtype=float)

        return riesgo_residual_sim, perdidas_usd_sim, correlations

    except Exception as e:
        print(f"Error en simular_montecarlo: {e}")
        return np.array([]), np.array([]), None


# --- 3. plotting.py ---
# Este módulo contendría las funciones para generar visualizaciones.

import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

def create_heatmap(df_risks, matriz_probabilidad, matriz_impacto, idioma="es"):
    """
    Crea un mapa de calor 5x5 basado en el riesgo residual promedio
    para combinaciones de probabilidad de amenaza y rangos de impacto numérico.

    Args:
        df_risks (pd.DataFrame): DataFrame con los riesgos evaluados.
        matriz_probabilidad (pd.DataFrame): DataFrame con las clasificaciones de probabilidad.
        matriz_impacto (pd.DataFrame): DataFrame con las clasificaciones de impacto.
        idioma (str): Idioma para las etiquetas ('es' o 'en').

    Returns:
        plotly.graph_objects.Figure: Objeto Figure de Plotly para el mapa de calor, o None si no hay riesgos.
    """
    if df_risks.empty:
        return None

    prob_bins = [0] + matriz_probabilidad['Valor'].tolist() + [1.0]
    prob_labels = matriz_probabilidad['Clasificacion'].tolist()

    impact_bins = [0, 20, 40, 60, 80, 100]
    impact_labels_es = ['Muy Bajo (0-20)', 'Bajo (21-40)', 'Medio (41-60)', 'Alto (61-80)', 'Muy Alto (81-100)']
    impact_labels_en = ['Very Low (0-20)', 'Low (21-40)', 'Medium (41-60)', 'High (61-80)', 'Very High (81-100)']
    impact_labels = impact_labels_es if idioma == "es" else impact_labels_en

    df_risks_copy = df_risks.copy()
    df_risks_copy['Prob_Bin'] = pd.cut(df_risks_copy['Probabilidad'], bins=prob_bins, labels=prob_labels, right=True, include_lowest=True)
    df_risks_copy['Impact_Bin'] = pd.cut(df_risks_copy['Impacto Numérico'], bins=impact_bins, labels=impact_labels, right=True, include_lowest=True)

    pivot_table = df_risks_copy.pivot_table(values='Riesgo Residual', index='Prob_Bin', columns='Impact_Bin', aggfunc='mean')
    pivot_table = pivot_table.reindex(index=prob_labels, columns=impact_labels)

    z_values = pivot_table.values.tolist()
    text_values = []
    
    for r in range(len(prob_labels)):
        row_text = []
        for c in range(len(impact_labels)):
            val = pivot_table.iloc[r, c]
            if pd.isna(val):
                row_text.append('N/A')
            else:
                for v_min, v_max, clasif_es, color, clasif_en in criticidad_límites:
                    if v_min <= val <= v_max:
                        row_text.append(f"{val:.2f}\n" + (clasif_es if idioma == "es" else clasif_en))
                        break
        text_values.append(row_text)

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=impact_labels,
        y=prob_labels,
        text=text_values,
        texttemplate="%{text}",
        hoverinfo="text",
        colorscale=[[limit[0], limit[3]] for limit in criticidad_límites],
        showscale=True,
        colorbar=dict(
            title=('Riesgo Residual Promedio' if idioma == "es" else 'Average Residual Risk'),
            tickvals=[(l[0]+l[1])/2 for l in criticidad_límites],
            ticktext=[(l[2] if idioma == "es" else l[4]) for l in criticidad_límites],
            lenmode="fraction", len=0.75, yanchor="middle", y=0.5
        )
    ))

    fig.update_layout(
        title=('Mapa de Calor de Riesgos (Riesgo Residual Promedio)' if idioma == "es" else 'Risk Heatmap (Average Residual Risk)'),
        xaxis_title=('Impacto Numérico' if idioma == "es" else 'Numeric Impact'),
        yaxis_title=('Probabilidad de Amenaza' if idioma == "es" else 'Threat Probability'),
        xaxis=dict(side='top'),
        height=450,
        margin=dict(t=80, b=20)
    )
    return fig


def create_pareto_chart(df_risks, idioma="es"):
    """
    Crea un gráfico de Pareto para los riesgos, mostrando el riesgo residual y el porcentaje acumulado.

    Args:
        df_risks (pd.DataFrame): DataFrame con los riesgos evaluados.
        idioma (str): Idioma para las etiquetas ('es' o 'en').

    Returns:
        plotly.graph_objects.Figure: Objeto Figure de Plotly para el gráfico de Pareto, o None si no hay riesgos.
    """
    if df_risks.empty:
        return None

    df_sorted = df_risks.sort_values(by='Riesgo Residual', ascending=False).copy()
    df_sorted['Riesgo Residual Acumulado'] = df_sorted['Riesgo Residual'].cumsum()
    df_sorted['Porcentaje Acumulado'] = (df_sorted['Riesgo Residual Acumulado'] / df_sorted['Riesgo Residual'].sum()) * 100

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_sorted['Nombre del Riesgo'],
        y=df_sorted['Riesgo Residual'],
        name=('Riesgo Residual' if idioma == "es" else 'Residual Risk'),
        marker_color='#1f77b4'
    ))

    fig.add_trace(go.Scatter(
        x=df_sorted['Nombre del Riesgo'],
        y=df_sorted['Porcentaje Acumulado'],
        mode='lines+markers',
        name=('Porcentaje Acumulado' if idioma == "es" else 'Cumulative Percentage'),
        yaxis='y2',
        marker_color='#d62728'
    ))

    fig.update_layout(
        title=('Gráfico de Pareto de Riesgos' if idioma == "es" else 'Risk Pareto Chart'),
        xaxis_title=('Nombre del Riesgo' if idioma == "es" else 'Risk Name'),
        yaxis_title=('Riesgo Residual' if idioma == "es" else 'Residual Risk'),
        yaxis2=dict(
            title=('Porcentaje Acumulado' if idioma == "es" else 'Cumulative Percentage'),
            overlaying='y',
            side='right',
            range=[0, 100],
            tickvals=np.arange(0, 101, 10)
        ),
        legend=dict(x=0.01, y=0.99),
        height=450,
        margin=dict(t=80, b=20)
    )
    return fig

def plot_montecarlo_histogram(data, title, x_label, idioma="es"):
    """
    Crea un histograma para los datos de la simulación Monte Carlo.

    Args:
        data (np.array): Array de datos simulados.
        title (str): Título del histograma.
        x_label (str): Etiqueta del eje X.
        idioma (str): Idioma para las etiquetas ('es' o 'en').

    Returns:
        matplotlib.figure.Figure: Objeto Figure de Matplotlib para el histograma, o None si no hay datos.
    """
    if data is None or len(data) == 0:
        return None

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data, kde=True, ax=ax, color='#28a745')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel('Frecuencia' if idioma == "es" else 'Frequency')
    plt.tight_layout()
    return fig

def create_sensitivity_plot(correlations, idioma="es"):
    """
    Crea un gráfico de barras para el análisis de sensibilidad.

    Args:
        correlations (pd.Series): Serie de correlaciones entre factores y pérdida económica.
        idioma (str): Idioma para las etiquetas ('es' o 'en').

    Returns:
        plotly.graph_objects.Figure: Objeto Figure de Plotly para el gráfico de sensibilidad, o None si no hay correlaciones.
    """
    if correlations is None or correlations.empty:
        return None

    fig = px.bar(
        x=correlations.index,
        y=correlations.values,
        title=('Análisis de Sensibilidad: Correlación con Pérdida Económica' if idioma == "es" else 'Sensitivity Analysis: Correlation with Economic Loss'),
        labels={
            'x': ('Factor de Riesgo' if idioma == "es" else 'Risk Factor'),
            'y': ('Magnitud de Correlación' if idioma == "es" else 'Correlation Magnitude')
        },
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig.update_layout(xaxis_tickangle=-45, height=400, margin=dict(t=80, b=20))
    return fig


# --- 4. utils.py ---
# Este módulo contendría funciones de utilidad para la interfaz de usuario.

import streamlit as st
# Las importaciones de data_config se harían aquí si fuera un archivo separado
# from data_config import criticidad_límites

def reset_form_fields():
    """Reinicia los campos del formulario de entrada de riesgo en Streamlit."""
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

    Args:
        df_risks (pd.DataFrame): DataFrame con los riesgos evaluados.
        idioma (str): Idioma para la clasificación de criticidad.

    Returns:
        pandas.io.formats.style.Styler: Objeto Styler de Pandas con el formato aplicado.
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

# --- 5. main_app.py ---
# Este es el archivo principal de la aplicación Streamlit.

import streamlit as st
# Asumiendo que data_config, calculations, plotting y utils son módulos en el mismo directorio.
# Si estuvieran en archivos separados, se importarían así:
# from data_config import tabla_tipo_impacto, matriz_probabilidad, matriz_impacto, factor_exposicion, factor_probabilidad, efectividad_controles, criticidad_límites, textos
# from calculations import clasificar_criticidad, calcular_criticidad, simular_montecarlo
# from plotting import create_heatmap, create_pareto_chart, plot_montecarlo_histogram, create_sensitivity_plot
# from utils import reset_form_fields, format_risk_dataframe

# --- Configuración de la página ---
st.set_page_config(layout="wide", page_title="Calculadora de Riesgos", page_icon="🛡️")

# --- CSS Personalizado ---
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stSelectbox>div>div {
        border-radius: 8px;
    }
    .stSlider > div > div:first-child {
        color: #4CAF50;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid #4CAF50;
    }
    .metric-box h3 {
        color: #333;
        font-size: 1em;
        margin-bottom: 5px;
    }
    .metric-box p {
        font-size: 1.2em;
        font-weight: bold;
        color: #000;
    }
    .stAlert {
        border-radius: 8px;
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
    st.session_state.current_edit_index = -1 # -1 significa que no estamos editando

# Valores por defecto para reiniciar el formulario
if 'default_type_impact' not in st.session_state:
    st.session_state['default_type_impact'] = tabla_tipo_impacto['Tipo de Impacto'].iloc[0]
if 'default_probabilidad' not in st.session_state:
    st.session_state['default_probabilidad'] = factor_probabilidad['Clasificacion'].iloc[0]
if 'default_exposicion' not in st.session_state:
    st.session_state['default_exposicion'] = factor_exposicion['Clasificacion'].iloc[0]
if 'default_impacto_numerico' not in st.session_state:
    st.session_state['default_impacto_numerico'] = 50
if 'default_control_effectiveness' not in st.session_state:
    st.session_state['default_control_effectiveness'] = 50

# --- Función para obtener textos en el idioma actual ---
def get_text(key):
    return textos[st.session_state.idioma].get(key, key)

# --- Sidebar para selección de idioma y texto de impuestos ---
with st.sidebar:
    # Toggle de idioma
    if st.checkbox(get_text("sidebar_language_toggle"), value=(st.session_state.idioma == 'en')):
        st.session_state.idioma = 'en'
    else:
        st.session_state.idioma = 'es'

    st.markdown("---")
    st.header(get_text("tax_info_title"))
    st.info(get_text("tax_info_text"))

# --- Título de la Aplicación ---
st.title(get_text("app_title"))
st.markdown("---")

# --- Contenido Principal de la Aplicación (Two Columns) ---
col_form, col_graf = st.columns([1, 1.5]) # Ajustar proporciones de columnas

with col_form:
    st.header(get_text("risk_input_form_title"))

    # Inputs del formulario de riesgo
    with st.form("risk_form", clear_on_submit=False):
        risk_name = st.text_input(get_text("risk_name"),
                                    key="risk_name_input",
                                    value=st.session_state.get('risk_name_input', ''))
        risk_description = st.text_area(get_text("risk_description"),
                                        key="risk_description_input",
                                        value=st.session_state.get('risk_description_input', ''))

        selected_type_impact = st.selectbox(
            get_text("risk_type_impact"),
            tabla_tipo_impacto['Tipo de Impacto'],
            format_func=lambda x: f"{x} (Ponderación: {tabla_tipo_impacto[tabla_tipo_impacto['Tipo de Impacto'] == x]['Ponderación'].iloc[0]})",
            key="selected_type_impact"
        )
        selected_probabilidad_clasificacion = st.selectbox(
            get_text("risk_probability"),
            factor_probabilidad['Clasificacion'],
            format_func=lambda x: f"{x} ({factor_probabilidad[factor_probabilidad['Clasificacion'] == x]['Definición'].iloc[0]})",
            key="selected_probabilidad"
        )
        selected_exposicion_clasificacion = st.selectbox(
            get_text("risk_exposure"),
            factor_exposicion['Clasificacion'],
            format_func=lambda x: f"{x} ({factor_exposicion[factor_exposicion['Clasificacion'] == x]['Definición'].iloc[0]})",
            key="selected_exposicion"
        )

        # Slider para Impacto Numérico (0-100)
        impacto_numerico_slider = st.slider(
            get_text("risk_impact_numeric"),
            min_value=0, max_value=100, value=st.session_state.get('impacto_numerico_slider', 50), step=1,
            help="Valor numérico del impacto del riesgo, donde 0 es insignificante y 100 es catastrófico.",
            key="impacto_numerico_slider"
        )

        # Slider para Efectividad del Control (%)
        control_effectiveness_slider = st.slider(
            get_text("risk_control_effectiveness"),
            min_value=0, max_value=100, value=st.session_state.get('control_effectiveness_slider', 50), step=1,
            help="Porcentaje de efectividad de los controles existentes para mitigar el riesgo.",
            key="control_effectiveness_slider"
        )

        deliberate_threat_checkbox = st.checkbox(get_text("risk_deliberate_threat"),
                                                  value=st.session_state.get('deliberate_threat_checkbox', False),
                                                  key="deliberate_threat_checkbox")

        submitted = st.form_submit_button(get_text("add_risk_button"))

        if submitted:
            if not risk_name:
                st.error(get_text("error_risk_name_empty"))
            else:
                probabilidad_factor = factor_probabilidad[factor_probabilidad['Clasificacion'] == selected_probabilidad_clasificacion]['Factor'].iloc[0]
                exposicion_factor = factor_exposicion[factor_exposicion['Clasificacion'] == selected_exposicion_clasificacion]['Factor'].iloc[0]
                amenaza_deliberada_factor_val = 1 if deliberate_threat_checkbox else 0 # 1 para SI, 0 para NO
                ponderacion_impacto_val = tabla_tipo_impacto[tabla_tipo_impacto['Tipo de Impacto'] == selected_type_impact]['Ponderación'].iloc[0]

                amenaza_inherente_det, amenaza_residual_det, amenaza_residual_ajustada_det, riesgo_residual_det = \
                    calcular_criticidad(
                        probabilidad_factor,
                        exposicion_factor,
                        amenaza_deliberada_factor_val,
                        control_effectiveness_slider, # Se envía como porcentaje, la función lo convierte
                        impacto_numerico_slider, # Se envía como 0-100
                        ponderacion_impacto_val
                    )

                clasificacion_det, color_det = clasificar_criticidad(riesgo_residual_det, st.session_state.idioma)

                # Si estamos editando, actualizamos el riesgo existente
                if st.session_state.current_edit_index != -1:
                    idx = st.session_state.current_edit_index
                    st.session_state.riesgos.loc[idx] = [
                        st.session_state.riesgos.loc[idx, 'ID'], # Mantener el ID existente
                        risk_name,
                        risk_description,
                        selected_type_impact,
                        probabilidad_factor, # Guardar el factor numérico
                        exposicion_factor,   # Guardar el factor numérico
                        impacto_numerico_slider,
                        control_effectiveness_slider,
                        "Sí" if deliberate_threat_checkbox else "No",
                        f"{amenaza_inherente_det:.2f}",
                        f"{amenaza_residual_det:.2f}",
                        f"{amenaza_residual_ajustada_det:.2f}",
                        riesgo_residual_det,
                        clasificacion_det,
                        color_det
                    ]
                    st.success(f"{get_text('risk_name').replace(':', '')} '{risk_name}' actualizado exitosamente.")
                    st.session_state.current_edit_index = -1 # Salir del modo edición
                    reset_form_fields() # Limpiar el formulario después de editar
                else:
                    # Crear nuevo riesgo
                    new_risk_id = len(st.session_state.riesgos) + 1
                    new_risk = {
                        "ID": new_risk_id,
                        "Nombre del Riesgo": risk_name,
                        "Descripción": risk_description,
                        "Tipo de Impacto": selected_type_impact,
                        "Probabilidad": probabilidad_factor,
                        "Exposición": exposicion_factor,
                        "Impacto Numérico": impacto_numerico_slider,
                        "Efectividad del Control (%)": control_effectiveness_slider,
                        "Amenaza Deliberada": "Sí" if deliberate_threat_checkbox else "No",
                        "Amenaza Inherente": f"{amenaza_inherente_det:.2f}",
                        "Amenaza Residual": f"{amenaza_residual_det:.2f}",
                        "Amenaza Residual Ajustada": f"{amenaza_residual_ajustada_det:.2f}",
                        "Riesgo Residual": riesgo_residual_det,
                        "Clasificación": clasificacion_det,
                        "Color": color_det
                    }
                    st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([new_risk])], ignore_index=True)
                    st.success(get_text("success_risk_added"))
                    reset_form_fields() # Limpiar el formulario después de agregar

    st.markdown("---")
    st.header(get_text("deterministic_results_title"))
    # Mostrar resultados del modelo determinista actual
    if 'riesgo_residual_det' in locals():
        col1_det, col2_det = st.columns(2)
        with col1_det:
            st.markdown(f"<div class='metric-box'><h3>{get_text('inherent_threat')}</h3><p>{amenaza_inherente_det:.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('residual_threat')}</h3><p>{amenaza_residual_det:.2f}</p></div>", unsafe_allow_html=True)
        with col2_det:
            st.markdown(f"<div class='metric-box'><h3>{get_text('adjusted_residual_threat')}</h3><p>{amenaza_residual_ajustada_det:.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('residual_risk')}</h3><p>{riesgo_residual_det:.2f}</p></div>", unsafe_allow_html=True)

        st.markdown(f"<p style='text-align: center; font-size: 1.2em; font-weight: bold;'>{get_text('classification')}: <span style='color:{color_det};'>{clasificacion_det}</span></p>", unsafe_allow_html=True)
    else:
        st.info("Ingresa los datos del riesgo para ver los resultados deterministas aquí.")

    st.markdown("---")
    st.header(get_text("added_risks_title"))
    if not st.session_state.riesgos.empty:
        # Añadir botones de editar/eliminar
        df_display = st.session_state.riesgos.copy()
        df_display['Acciones'] = '' # Columna dummy para los botones

        for i, row in df_display.iterrows():
            edit_button_key = f"edit_btn_{row['ID']}"
            delete_button_key = f"del_btn_{row['ID']}"

            col_btns = st.columns([1,1,10]) # Ajustar el ancho para los botones
            with col_btns[0]:
                if st.button(get_text("edit_risk"), key=edit_button_key):
                    st.session_state.current_edit_index = i
                    st.session_state.risk_name_input = row['Nombre del Riesgo']
                    st.session_state.risk_description_input = row['Descripción']
                    st.session_state.selected_type_impact = row['Tipo de Impacto']
                    
                    # Para la probabilidad y exposición, necesitamos el valor de clasificación para el selectbox
                    st.session_state.selected_probabilidad = factor_probabilidad[factor_probabilidad['Factor'] == row['Probabilidad']]['Clasificacion'].iloc[0]
                    st.session_state.selected_exposicion = factor_exposicion[factor_exposicion['Factor'] == row['Exposición']]['Clasificacion'].iloc[0]
                    
                    st.session_state.impacto_numerico_slider = row['Impacto Numérico']
                    st.session_state.control_effectiveness_slider = row['Efectividad del Control (%)']
                    st.session_state.deliberate_threat_checkbox = (row['Amenaza Deliberada'] == 'Sí')
                    st.rerun() # Volver a ejecutar para cargar los datos en el formulario
            with col_btns[1]:
                if st.button(get_text("delete_risk"), key=delete_button_key):
                    if st.session_state.idioma == "es":
                        if st.warning(get_text("confirm_delete")):
                            st.session_state.riesgos = st.session_state.riesgos.drop(i).reset_index(drop=True)
                            st.success(get_text("risk_deleted"))
                            st.rerun()
                    else: # English confirmation
                        if st.warning(get_text("confirm_delete")):
                            st.session_state.riesgos = st.session_state.riesgos.drop(i).reset_index(drop=True)
                            st.success(get_text("risk_deleted"))
                            st.rerun()

        st.dataframe(format_risk_dataframe(st.session_state.riesgos, st.session_state.idioma), hide_index=True)
        
        csv_data = st.session_state.riesgos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=get_text("download_excel_button"),
            data=csv_data,
            file_name="riesgos_evaluados.csv",
            mime="text/csv",
            help="Descargar los datos de los riesgos evaluados en formato CSV."
        )
    else:
        st.info(get_text("no_risks_yet"))

    st.markdown("---")
    st.header(get_text("montecarlo_input_title"))
    # Asegurarse de que haya un riesgo determinista calculado para activar la simulación
    if 'riesgo_residual_det' in locals():
        valor_economico = st.number_input(
            get_text("economic_value_asset"),
            min_value=0.0, value=100000.0, step=1000.0, format="%.2f",
            help="Valor monetario del activo o impacto total esperado en USD."
        )
        num_iteraciones = st.slider(
            get_text("num_iterations"),
            min_value=1000, max_value=50000, value=10000, step=1000,
            help="Número de simulaciones para el cálculo Monte Carlo."
        )

        if valor_economico == 0:
            st.warning(get_text("economic_value_asset") + " es 0. Las pérdidas simuladas serán 0.")

        if st.button(get_text("run_montecarlo_button")):
            with st.spinner('Ejecutando simulación Monte Carlo...'):
                probabilidad_base_mc = probabilidad_factor
                exposicion_base_mc = exposicion_factor
                impacto_numerico_base_mc = impacto_numerico_slider # Usamos el slider para el base
                efectividad_base_pct_mc = control_effectiveness_slider
                amenaza_deliberada_factor_mc = amenaza_deliberada_factor_val
                ponderacion_impacto_mc = ponderacion_impacto_val # Se envía sin normalizar aquí

                riesgo_residual_sim_data, perdidas_usd_sim_data, correlations = simular_montecarlo(
                    probabilidad_base_mc, exposicion_base_mc, impacto_numerico_base_mc,
                    efectividad_base_pct_mc, amenaza_deliberada_factor_mc, ponderacion_impacto_mc,
                    valor_economico, num_iteraciones
                )
                
                if perdidas_usd_sim_data is not None and len(perdidas_usd_sim_data) > 0:
                    st.session_state.riesgo_residual_sim_data = riesgo_residual_sim_data
                    st.session_state.perdidas_usd_sim_data = perdidas_usd_sim_data
                    st.session_state.montecarlo_correlations = correlations
                else:
                    st.error("No se pudieron generar resultados de Monte Carlo. Verifique los valores de entrada.")

    else:
        st.info("Primero calcula un riesgo en la sección superior para habilitar la simulación Monte Carlo.")

    # Histograma de Monte Carlo (Pérdida Económica)
    st.markdown("---")
    if 'perdidas_usd_sim_data' in st.session_state and len(st.session_state.perdidas_usd_sim_data) > 0:
        st.header(get_text("economic_loss_distribution_title"))
        fig_loss = plot_montecarlo_histogram(st.session_state.perdidas_usd_sim_data, get_text("economic_loss_distribution_title"), get_text("economic_value_asset"), st.session_state.idioma)
        if fig_loss:
            col_left_hist, col_center_hist, col_right_hist = st.columns([1,3,1])
            with col_center_hist:
                st.pyplot(fig_loss)
                plt.close(fig_loss) # Cierra la figura para liberar memoria
    else:
        st.info("Ejecuta la simulación Monte Carlo para ver la distribución de pérdidas económicas.")


with col_graf:
    # Mapa de Calor de Riesgos (5x5)
    st.header(get_text("risk_heatmap_title"))
    if not st.session_state.riesgos.empty:
        fig_heatmap = create_heatmap(st.session_state.riesgos, matriz_probabilidad, matriz_impacto, st.session_state.idioma)
        if fig_heatmap:
            st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.info("Agrega riesgos para generar el mapa de calor.")

    st.markdown("---")
    # Gráfico de Pareto de Riesgos
    st.header(get_text("risk_pareto_chart_title"))
    if not st.session_state.riesgos.empty:
        fig_pareto = create_pareto_chart(st.session_state.riesgos, st.session_state.idioma)
        if fig_pareto:
            st.plotly_chart(fig_pareto, use_container_width=True)
    else:
        st.info("Agrega riesgos para generar el gráfico de Pareto.")

    st.markdown("---")
    # Resultados y Métricas de Monte Carlo
    st.header(get_text("montecarlo_results_title"))
    if 'perdidas_usd_sim_data' in st.session_state and len(st.session_state.perdidas_usd_sim_data) > 0:
        perdidas = st.session_state.perdidas_usd_sim_data
        
        # Calcular CVaR (Expected Shortfall)
        alpha = 0.95 # Para CVaR 95%
        # Ordenar las pérdidas y tomar el (1-alpha) superior
        sorted_losses = np.sort(perdidas)
        index_cvar = int(np.floor(len(sorted_losses) * alpha))
        cvar_95_val = sorted_losses[index_cvar:].mean()

        col_mc1, col_mc2 = st.columns(2)
        with col_mc1:
            st.markdown(f"<div class='metric-box'><h3>{get_text('expected_loss')}</h3><p>${np.mean(perdidas):,.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('median_loss')}</h3><p>${np.median(perdidas):,.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('p5_loss')}</h3><p>${np.percentile(perdidas, 5):,.2f}</p></div>", unsafe_allow_html=True)
        with col_mc2:
            st.markdown(f"<div class='metric-box'><h3>{get_text('p90_loss')}</h3><p>${np.percentile(perdidas, 90):,.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('max_loss')}</h3><p>${np.max(perdidas):,.2f}</p></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='metric-box'><h3>{get_text('cvar_95')}</h3><p>${cvar_95_val:,.2f}</p></div>", unsafe_allow_html=True)

        st.markdown("---")
        st.header(get_text("sensitivity_analysis_title"))
        if 'montecarlo_correlations' in st.session_state and st.session_state.montecarlo_correlations is not None:
            fig_sensitivity = create_sensitivity_plot(st.session_state.montecarlo_correlations, st.session_state.idioma)
            if fig_sensitivity:
                st.plotly_chart(fig_sensitivity, use_container_width=True)
        else:
            st.info("Ejecuta la simulación Monte Carlo para ver el análisis de sensibilidad.")
    else:
        st.info("Ejecuta la simulación Monte Carlo para ver los resultados aquí.")
