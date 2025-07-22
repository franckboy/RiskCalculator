import numpy as np
import pandas as pd
from data_config import criticidad_límites # Importar desde el nuevo archivo

def clasificar_criticidad(valor, idioma="es"):
    """
    Clasifica un valor numérico de riesgo en una categoría de criticidad
    y asigna un color asociado.
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
    """
    try:
        # Asegurarse de que los valores numéricos estén en el rango correcto
        probabilidad = float(probabilidad)
        exposicion = float(exposicion)
        amenaza_deliberada_factor = float(amenaza_deliberada_factor)
        efectividad = float(efectividad) / 100.0 # Convertir porcentaje a factor (0-1)
        valor_impacto_numerico = float(valor_impacto_numerico)
        ponderacion_impacto = float(ponderacion_impacto)

        # Normalizar el impacto numérico y la ponderación para la fórmula
        # El impacto numérico (0-100) se normaliza a un factor de 0-1
        impacto_norm = valor_impacto_numerico / 100.0 if valor_impacto_numerico > 0 else 0
        # La ponderación del impacto (ej. 25 para humano) se normaliza a un factor de 0-1
        ponderacion_factor = ponderacion_impacto / 100.0

        # Cálculos de riesgo
        amenaza_inherente = probabilidad * exposicion
        amenaza_residual = amenaza_inherente * (1 - efectividad)

        # Si amenaza_deliberada_factor es 0 (No), no ajusta; si es 1 (Sí), multiplica
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor) # Si es 0, es 1, si es 1, es 2
        # Considerar si quieres que una amenaza deliberada multiplique por 1 (es decir, el mismo valor si es 'Si')
        # o por un factor mayor a 1. Aquí, 1 para 'Sí' significa que no se ajusta, 2 para 'Sí' lo duplica.
        # Ajuste a la lógica original: si amenaza_deliberada_factor es 1 (Sí), duplica amenaza_residual
        # Si es 0 (No), mantiene amenaza_residual.
        amenaza_residual_ajustada = amenaza_residual * (1 + amenaza_deliberada_factor)

        # El riesgo residual final se calcula combinando la amenaza ajustada con el impacto y la ponderación
        riesgo_residual = amenaza_residual_ajustada * impacto_norm * ponderacion_factor

        # Asegurar que el riesgo residual no exceda 1
        riesgo_residual = np.clip(riesgo_residual, 0, 1)

        return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

    except Exception as e:
        print(f"Error en calcular_criticidad: {e}")
        return 0.0, 0.0, 0.0, 0.0 # Retornar valores seguros en caso de error

def simular_montecarlo(probabilidad_base, exposicion_base, impacto_numerico_base, efectividad_base_pct, amenaza_deliberada_factor_base, ponderacion_impacto, valor_economico, iteraciones=10000):
    """
    Ejecuta una simulación Monte Carlo para el cálculo de riesgos y pérdidas económicas.
    """
    if valor_economico <= 0:
        return np.array([]), np.array([]), None, None # Retornar arrays vacíos si el valor económico es 0 o negativo

    try:
        # Convertir efectividad de porcentaje a factor
        efectividad_base = efectividad_base_pct / 100.0
        
        # Parámetros de variabilidad para cada factor (desviación estándar)
        # Ajustar sigmas según la incertidumbre deseada
        sigma_probabilidad = 0.1 # Pequeña variabilidad para probabilidades
        sigma_exposicion = 0.1
        sigma_impacto_norm = 0.05 # Menor variabilidad para impacto ya normalizado 0-1
        sigma_efectividad = 0.1
        # sigma_amenaza_deliberada = 0 # Normalmente binario, no se simula variabilidad aquí

        # Impacto monetario (USD)
        # Si el impacto_numerico_base va de 0-100, se puede mapear a un rango de pérdida monetaria
        # Por ejemplo, un impacto de 100 significa el 100% del valor económico se pierde.
        # Vamos a asumir que el 'impacto_numerico_base' de 0-100 es un porcentaje de daño al 'valor_economico'
        # o que el usuario introducirá V_min y V_max para las pérdidas, como en la petición.

        # Nueva lógica para el impacto de Monte Carlo: rangos en USD
        # Usaremos el impacto_numerico_base (0-100) para definir un rango de pérdida monetaria base.
        # Por ejemplo, si impacto_numerico_base es 50, la pérdida base es 50% del valor económico.
        # Luego, simulamos alrededor de ese valor base.
        # Definiremos un rango de incertidumbre para la pérdida monetaria.
        
        # Transformamos el impacto numérico base (0-100) en un porcentaje del valor económico
        # Esto es un factor base para la pérdida económica.
        factor_perdida_base = impacto_numerico_base / 100.0

        # Definimos un rango de incertidumbre para este factor de pérdida monetaria.
        # Por ejemplo, +/- 20% del factor de pérdida base.
        sigma_factor_perdida = 0.20 * factor_perdida_base
        if sigma_factor_perdida == 0 and factor_perdida_base > 0: # Evitar sigma 0 si hay impacto
             sigma_factor_perdida = 0.05 # Mínima variabilidad si el impacto es bajo pero existente
        elif factor_perdida_base == 0:
            sigma_factor_perdida = 0 # No hay variabilidad si no hay impacto base

        # Arrays para almacenar los resultados de la simulación
        riesgo_residual_sim = np.zeros(iteraciones)
        perdidas_usd_sim = np.zeros(iteraciones)

        for i in range(iteraciones):
            # Generar valores aleatorios para cada parámetro usando una distribución normal
            # y asegurándose de que estén dentro de rangos lógicos [0,1] o [1,100]
            probabilidad_sim = np.clip(np.random.normal(probabilidad_base, sigma_probabilidad), 0.01, 1.0)
            exposicion_sim = np.clip(np.random.normal(exposicion_base, sigma_exposicion), 0.01, 1.0)
            efectividad_sim = np.clip(np.random.normal(efectividad_base, sigma_efectividad), 0.0, 1.0)

            # Simular el factor de pérdida monetaria
            sim_factor_perdida = np.clip(np.random.normal(factor_perdida_base, sigma_factor_perdida), 0.0, 1.0)
            
            # Recalcular impacto_norm para la simulación
            # Usamos el factor de pérdida simulado como el impacto_norm para la fórmula
            impacto_norm_sim = sim_factor_perdida

            # Amenaza deliberada se mantiene base o se puede introducir una probabilidad binaria
            amenaza_deliberada_sim = amenaza_deliberada_factor_base # Asumimos que no varía en la simulación a menos que se indique

            # Reutilizar la lógica de cálculo de riesgo con los valores simulados
            amenaza_inherente_sim = probabilidad_sim * exposicion_sim
            amenaza_residual_sim = amenaza_inherente_sim * (1 - efectividad_sim)
            amenaza_residual_ajustada_sim = amenaza_residual_sim * (1 + amenaza_deliberada_sim)
            
            # Calcular el riesgo residual simulado
            riesgo_residual_iter = amenaza_residual_ajustada_sim * impacto_norm_sim * (ponderacion_impacto / 100.0)
            riesgo_residual_sim[i] = np.clip(riesgo_residual_iter, 0, 1)

            # Calcular la pérdida económica simulada
            perdidas_usd_sim[i] = riesgo_residual_sim[i] * valor_economico # El riesgo residual es un índice de criticidad que se aplica al valor económico

        # Calcular correlaciones para análisis de sensibilidad
        df_sim = pd.DataFrame({
            'probabilidad': np.array([np.random.normal(probabilidad_base, sigma_probabilidad) for _ in range(iteraciones)]),
            'exposicion': np.array([np.random.normal(exposicion_base, sigma_exposicion) for _ in range(iteraciones)]),
            'impacto_norm': np.array([np.random.normal(factor_perdida_base, sigma_factor_perdida) for _ in range(iteraciones)]),
            'efectividad': np.array([np.random.normal(efectividad_base, sigma_efectividad) for _ in range(iteraciones)]),
            'perdida_usd': perdidas_usd_sim
        })
        
        # Calcular correlaciones de Pearson con la pérdida económica
        # Asegurarse de que las columnas tengan varianza para calcular correlación
        valid_cols = [col for col in ['probabilidad', 'exposicion', 'impacto_norm', 'efectividad'] if df_sim[col].std() > 0]
        
        if valid_cols:
            correlations = df_sim[valid_cols + ['perdida_usd']].corr(method='pearson')['perdida_usd'].drop('perdida_usd').abs().sort_values(ascending=False)
        else:
            correlations = pd.Series(dtype=float) # No hay columnas válidas para correlación

        # Correlación de Spearman puede ser más robusta para relaciones no lineales
        # correlations_spearman = df_sim[valid_cols + ['perdida_usd']].corr(method='spearman')['perdida_usd'].drop('perdida_usd').abs().sort_values(ascending=False)

        return riesgo_residual_sim, perdidas_usd_sim, correlations #, correlations_spearman

    except Exception as e:
        print(f"Error en simular_montecarlo: {e}")
        return np.array([]), np.array([]), None, None # Retornar arrays vacíos y None para correlaciones
