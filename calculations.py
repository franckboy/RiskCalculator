# calculations.py

import numpy as np
import pandas as pd
from data_config import criticidad_límites

def clasificar_criticidad(valor, idioma="es"):
    """Clasifica un valor de riesgo según los límites definidos."""
    # Recorre la lista de tuplas de criticidad
    for v_min, v_max, clasificacion_es, color, clasificacion_en in criticidad_límites:
        # La condición v_min < valor <= v_max es robusta para los bordes.
        # Se añade un caso especial para el valor 0.0, que debe caer en la primera categoría.
        if (v_min < valor <= v_max) or (valor == 0.0 and v_min == 0.0):
            return (clasificacion_es if idioma == "es" else clasificacion_en), color
    return "DESCONOCIDO", "#cccccc"

def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada_factor, efectividad, valor_impacto_numerico, ponderacion_impacto):
    """Calcula el riesgo residual de forma determinista."""
    try:
        # Conversión segura de tipos
        probabilidad = float(probabilidad)
        exposicion = float(exposicion)
        amenaza_deliberada_factor = float(amenaza_deliberada_factor)
        efectividad_norm = float(efectividad) / 100.0
        impacto_norm = float(valor_impacto_numerico) / 100.0
        ponderacion_factor = float(ponderacion_impacto) / 100.0

        # Cálculo secuencial de las métricas de amenaza
        amenaza_inherente = probabilidad * exposicion
        amenaza_residual = amenaza_inherente * (1 - efectividad_norm)
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor)
        
        # Cálculo del riesgo residual
        riesgo_residual = amenaza_residual_ajustada * impacto_norm * ponderacion_factor
        
        # Asegura que el riesgo esté siempre en el rango [0, 1]
        riesgo_residual = np.clip(riesgo_residual, 0, 1)

        return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual
    except Exception as e:
        print(f"Error en calcular_criticidad: {e}")
        return 0.0, 0.0, 0.0, 0.0

def simular_montecarlo(probabilidad_base, exposicion_base, impacto_numerico_base, efectividad_base_pct, 
                       amenaza_deliberada_factor_base, ponderacion_impacto, valor_economico, iteraciones=10000):
    """Ejecuta una simulación de Monte Carlo para estimar pérdidas."""
    if valor_economico <= 0:
        return np.array([]), np.array([]), None

    try:
        # Parámetros de la simulación (desviaciones estándar para simular incertidumbre)
        efectividad_base = efectividad_base_pct / 100.0
        sigma = 0.1 # Desviación estándar genérica para la mayoría de los factores

        # Arrays para almacenar los resultados de cada iteración
        riesgo_residual_sim = np.zeros(iteraciones)
        perdidas_usd_sim = np.zeros(iteraciones)
        
        # Generar todas las variables aleatorias de una vez (más eficiente)
        prob_sim = np.clip(np.random.normal(probabilidad_base, sigma, iteraciones), 0.01, 1.0)
        expo_sim = np.clip(np.random.normal(exposicion_base, sigma, iteraciones), 0.01, 1.0)
        efec_sim = np.clip(np.random.normal(efectividad_base, sigma, iteraciones), 0.0, 1.0)
        imp_norm_sim = np.clip(np.random.normal(impacto_numerico_base / 100.0, sigma, iteraciones), 0.0, 1.0)

        # Calcular el riesgo y la pérdida para todas las iteraciones vectorialmente
        amenaza_inherente_s = prob_sim * expo_sim
        amenaza_residual_s = amenaza_inherente_s * (1 - efec_sim)
        amenaza_adj_s = amenaza_residual_s * (1 + amenaza_deliberada_factor_base)
        
        riesgo_residual_sim = np.clip(amenaza_adj_s * imp_norm_sim * (ponderacion_impacto / 100.0), 0, 1)
        perdidas_usd_sim = riesgo_residual_sim * valor_economico

        # Crear DataFrame para análisis de sensibilidad
        df_sim = pd.DataFrame({
            'probabilidad': prob_sim,
            'exposicion': expo_sim,
            'impacto_norm': imp_norm_sim,
            'efectividad': efec_sim,
            'perdida_usd': perdidas_usd_sim
        })
        
        # Calcular correlaciones para el análisis de sensibilidad
        correlations = df_sim.corr()['perdida_usd'].drop('perdida_usd').abs().sort_values(ascending=True)

        return riesgo_residual_sim, perdidas_usd_sim, correlations

    except Exception as e:
        print(f"Error en simular_montecarlo: {e}")
        return np.array([]), np.array([]), None
