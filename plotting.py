import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from data_config import criticidad_límites

def create_heatmap(df_risks, matriz_probabilidad, matriz_impacto, idioma="es"):
    if df_risks.empty:
        return None

    prob_bins = [0] + matriz_probabilidad['Valor'].tolist() + [1.0]
    prob_labels = matriz_probabilidad['Clasificacion'].tolist()
    
    impact_bins = [0, 20, 40, 60, 80, 100]
    impact_labels = ['Muy Bajo (0-20)', 'Bajo (21-40)', 'Medio (41-60)', 'Alto (61-80)', 'Muy Alto (81-100)'] if idioma == "es" else ['Very Low (0-20)', 'Low (21-40)', 'Medium (41-60)', 'High (61-80)', 'Very High (81-100)']

    df_risks_copy = df_risks.copy()
    df_risks_copy['Prob_Bin'] = pd.cut(df_risks_copy['Probabilidad'], bins=prob_bins, labels=prob_labels)
    df_risks_copy['Impact_Bin'] = pd.cut(df_risks_copy['Impacto Numérico'], bins=impact_bins, labels=impact_labels)

    pivot_table = df_risks_copy.pivot_table(values='Riesgo Residual', index='Prob_Bin', columns='Impact_Bin', aggfunc='mean')
    pivot_table = pivot_table.reindex(index=prob_labels, columns=impact_labels)

    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=impact_labels,
        y=prob_labels,
        colorscale=[[limit[0], limit[3]] for limit in criticidad_límites],
        colorbar=dict(
            title='Riesgo Residual Promedio' if idioma == "es" else 'Average Residual Risk',
            tickvals=[(l[0]+l[1])/2 for l in criticidad_límites],
            ticktext=[l[2] if idioma == "es" else l[4] for l in criticidad_límites]
        )
    ))

    fig.update_layout(
        title='Mapa de Calor de Riesgos' if idioma == "es" else 'Risk Heatmap',
        xaxis_title='Impacto Numérico' if idioma == "es" else 'Numeric Impact',
        yaxis_title='Probabilidad de Amenaza' if idioma == "es" else 'Threat Probability',
        height=450
    )
    return fig

def create_pareto_chart(df_risks, idioma="es"):
    if df_risks.empty:
        return None
    
    df_sorted = df_risks.sort_values('Riesgo Residual', ascending=False)
    df_sorted['Cumulative'] = df_sorted['Riesgo Residual'].cumsum() / df_sorted['Riesgo Residual'].sum() * 100
    
    fig = go.Figure()
    
    # Barras de riesgo residual
    fig.add_trace(go.Bar(
        x=df_sorted['Nombre del Riesgo'],
        y=df_sorted['Riesgo Residual'],
        name='Riesgo Residual',
        marker_color='#4CAF50'
    ))
    
    # Línea de porcentaje acumulado
    fig.add_trace(go.Scatter(
        x=df_sorted['Nombre del Riesgo'],
        y=df_sorted['Cumulative'],
        name='% Acumulado',
        yaxis='y2',
        line=dict(color='#FF5722', width=2)
    ))
    
    fig.update_layout(
        title='Análisis de Pareto de Riesgos' if idioma == "es" else 'Risk Pareto Analysis',
        xaxis_title='Riesgos',
        yaxis_title='Riesgo Residual' if idioma == "es" else 'Residual Risk',
        yaxis2=dict(
            title='Porcentaje Acumulado' if idioma == "es" else 'Cumulative Percentage',
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        hovermode='x unified',
        height=500
    )
    
    return fig

def plot_montecarlo_histogram(riesgo_residual_sim, perdidas_usd_sim, idioma="es"):
    if len(riesgo_residual_sim) == 0:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=riesgo_residual_sim,
        name='Distribución de Riesgo' if idioma == "es" else 'Risk Distribution',
        marker_color='#4CAF50',
        opacity=0.7
    ))
    
    fig.update_layout(
        title='Simulación Monte Carlo - Riesgo Residual' if idioma == "es" else 'Monte Carlo Simulation - Residual Risk',
        xaxis_title='Riesgo Residual' if idioma == "es" else 'Residual Risk',
        yaxis_title='Frecuencia' if idioma == "es" else 'Frequency',
        height=400
    )
    
    return fig

def create_sensitivity_plot(correlations, idioma="es"):
    if correlations is None:
        return None
    
    fig = go.Figure(go.Bar(
        x=correlations.values,
        y=correlations.index,
        orientation='h',
        marker_color='#2196F3'
    ))
    
    fig.update_layout(
        title='Análisis de Sensibilidad' if idioma == "es" else 'Sensitivity Analysis',
        xaxis_title='Correlación con Pérdidas' if idioma == "es" else 'Correlation with Losses',
        yaxis_title='Variable',
        height=300
    )
    
    return fig
