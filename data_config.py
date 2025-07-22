import pandas as pd
# Tablas base para el modelo de riesgo
tabla_tipo_impacto = pd.DataFrame({
    'Tipo de Impacto': ['Humano', 'Operacional', 'Económico', 'Reputacional', 'Legal'],
    'Ponderación': [25, 20, 30, 15, 10],
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
    'Valor': [1, 2, 3, 4, 5],
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
    'Factor': [0.1, 0.3, 0.7, 0.9],
    'Mitigacion': [
        'Los controles no reducen significativamente el riesgo.',
        'Los controles ofrecen una reducción limitada del riesgo.',
        'Los controles reducen el riesgo de manera considerable.',
        'Los controles casi eliminan el riesgo.'
    ]
})

criticidad_límites = [
    (0, 0.1, 'ACEPTABLE', '#28a745', 'ACCEPTABLE'),
    (0.1, 0.2, 'TOLERABLE', '#90EE90', 'TOLERABLE'),
    (0.2, 0.4, 'MODERADO', '#ffc107', 'MODERATE'),
    (0.4, 0.6, 'ALTO', '#fd7e14', 'HIGH'),
    (0.6, 1.0, 'CRÍTICO', '#dc3545', 'CRITICAL')
]

textos = {
    "es": {
        "sidebar_language_toggle": "English",
        "app_title": "Calculadora de Riesgos y Simulador Monte Carlo",
        # ... (resto de textos en español)
    },
    "en": {
        "sidebar_language_toggle": "Español",
        "app_title": "Risk Calculator and Monte Carlo Simulator",
        # ... (resto de textos en inglés)
    }
}
