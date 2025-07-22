import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from data_config import criticidad_límites, factor_probabilidad

def create_heatmap(df_risks, idioma="es"):
    """Crea un mapa de calor promediando el riesgo residual."""
    if df_risks.empty:
        return go.Figure()

    # Ejes del mapa de calor
    prob_labels = factor_probabilidad['Clasificacion'].tolist()
    impact_labels = [
        'Muy Bajo (0-20)', 'Bajo (21-40)', 'Medio (41-60)', 
        'Alto (61-80)', 'Muy Alto (81-100)'
    ]
    impact_bins = [0, 21, 41, 61, 81, 101]

    df_copy = df_risks.copy()
    df_copy['Impact_Bin'] = pd.cut(df_copy['Impacto Numérico'], bins=impact_bins, labels=impact_labels, right=False)

    pivot_table = df_copy.pivot_table(
        values='Riesgo Residual', 
        index='Probabilidad Texto', 
        columns='Impact_Bin', 
        aggfunc='mean'
    )
    pivot_table = pivot_table.reindex(index=prob_labels, columns=impact_labels)

    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=impact_labels,
        y=prob_labels,
        colorscale=[[limit[0], limit[3]] for limit in criticidad_límites],
        zmin=0, zmax=1,
        colorbar=dict(title='Riesgo Residual')
    ))

    fig.update_layout(
        xaxis_title='Impacto Numérico',
        yaxis_title='Probabilidad de Amenaza',
        height=450,
        yaxis=dict(categoryorder='array', categoryarray=prob_labels)
    )
    return fig

def create_pareto_chart(df_risks, idioma="es"):
    """Crea un gráfico de Pareto para priorizar riesgos."""
    if df_risks.empty:
        return go.Figure()
    
    df_sorted = df_risks.sort_values('Riesgo Residual', ascending=False)
    df_sorted['Cumulative'] = df_sorted['Riesgo Residual'].cumsum() / df_sorted['Riesgo Residual'].sum() * 100
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_sorted['Nombre del Riesgo'], y=df_sorted['Riesgo Residual'], name='Riesgo Residual'))
    fig.add_trace(go.Scatter(x=df_sorted['Nombre del Riesgo'], y=df_sorted['Cumulative'], name='% Acumulado', yaxis='y2', line=dict(color='#FF5722')))
    
    fig.update_layout(
        xaxis_title='Riesgos',
        yaxis_title='Nivel de Riesgo Residual',
        yaxis2=dict(title='Porcentaje Acumulado', overlaying='y', side='right', range=[0, 101]),
        hovermode='x unified',
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_montecarlo_histogram(perdidas_usd_sim, idioma="es"):
    """Crea un histograma de la distribución de pérdidas monetarias."""
    title_text = "Distribución de Pérdidas Potenciales" if idioma == "es" else "Potential Loss Distribution"
    xaxis_title_text = "Pérdida Estimada (USD)" if idioma == "es" else "Estimated Loss (USD)"
    yaxis_title_text = "Frecuencia" if idioma == "es" else "Frequency"

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=perdidas_usd_sim,
        name='Pérdidas',
        marker_color='#4CAF50',
        opacity=0.75,
        xbins=dict(start=0, end=max(perdidas_usd_sim) if len(perdidas_usd_sim) > 0 else 1, size=0) 
    ))
    
    fig.update_layout(
        title=title_text,
        xaxis_title=xaxis_title_text,
        yaxis_title=yaxis_title_text,
        height=400
    )
    return fig

def create_sensitivity_plot(correlations, idioma="es"):
    """Crea un gráfico de barras para el análisis de sensibilidad."""
    if correlations is None or correlations.empty:
        return go.Figure()
        
    title_text = "Análisis de Sensibilidad (Tornado)" if idioma == "es" else "Sensitivity Analysis (Tornado Plot)"
    xaxis_title_text = "Correlación con la Pérdida" if idioma == "es" else "Correlation with Loss"

    fig = go.Figure(go.Bar(
        x=correlations.values,
        y=correlations.index,
        orientation='h',
        marker_color='#2196F3'
    ))
    
    fig.update_layout(
        title=title_text,
        xaxis_title=xaxis_title_text,
        yaxis_title='Variable de Entrada',
        height=300
    )
    return fig
