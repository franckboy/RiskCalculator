import numpy as np
import pandas as pd
from data_config import criticidad_límites

def clasificar_criticidad(valor, idioma="es"):
    for v_min, v_max, clasificacion_es, color, clasificacion_en in criticidad_límites:
        if v_min <= valor <= v_max:
            return clasificacion_es if idioma == "es" else clasificacion_en, color
    return "DESCONOCIDO", "#cccccc"

def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada_factor, efectividad, valor_impacto_numerico, ponderacion_impacto):
    try:
        probabilidad = float(probabilidad)
        exposicion = float(exposicion)
        amenaza_deliberada_factor = float(amenaza_deliberada_factor)
        efectividad = float(efectividad) / 100.0
        valor_impacto_numerico = float(valor_impacto_numerico)
        ponderacion_impacto = float(ponderacion_impacto)

        impacto_norm = valor_impacto_numerico / 100.0 if valor_impacto_numerico > 0 else 0
        ponderacion_factor = ponderacion_impacto / 100.0

        amenaza_inherente = probabilidad * exposicion
        amenaza_residual = amenaza_inherente * (1 - efectividad)
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor)
        riesgo_residual = amenaza_residual_ajustada * impacto_norm * ponderacion_factor
        riesgo_residual = np.clip(riesgo_residual, 0, 1)

        return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual
    except Exception as e:
        print(f"Error en calcular_criticidad: {e}")
        return 0.0, 0.0, 0.0, 0.0

def simular_montecarlo(probabilidad_base, exposicion_base, impacto_numerico_base, efectividad_base_pct, 
                      amenaza_deliberada_factor_base, ponderacion_impacto, valor_economico, iteraciones=10000):
    if valor_economico <= 0:
        return np.array([]), np.array([]), None

    try:
        efectividad_base = efectividad_base_pct / 100.0
        sigma_probabilidad = 0.1
        sigma_exposicion = 0.1
        sigma_impacto_norm = 0.05
        sigma_efectividad = 0.1
        
        factor_perdida_base = impacto_numerico_base / 100.0
        sigma_factor_perdida = 0.20 * factor_perdida_base if factor_perdida_base > 0 else 0

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
            
            riesgo_residual_sim[i] = np.clip(amenaza_residual_ajustada_sim * impacto_norm_sim * (ponderacion_impacto / 100.0), 0, 1)
            perdidas_usd_sim[i] = riesgo_residual_sim[i] * valor_economico

        df_sim = pd.DataFrame({
            'probabilidad': np.random.normal(probabilidad_base, sigma_probabilidad, iteraciones),
            'exposicion': np.random.normal(exposicion_base, sigma_exposicion, iteraciones),
            'impacto_norm': np.random.normal(factor_perdida_base, sigma_factor_perdida, iteraciones),
            'efectividad': np.random.normal(efectividad_base, sigma_efectividad, iteraciones),
            'perdida_usd': perdidas_usd_sim
        })
        
        valid_cols = [col for col in ['probabilidad', 'exposicion', 'impacto_norm', 'efectividad'] if df_sim[col].std() > 0]
        correlations = df_sim[valid_cols + ['perdida_usd']].corr()['perdida_usd'].drop('perdida_usd').abs().sort_values(ascending=False)

        return riesgo_residual_sim, perdidas_usd_sim, correlations

    except Exception as e:
        print(f"Error en simular_montecarlo: {e}")
        return np.array([]), np.array([]), None
