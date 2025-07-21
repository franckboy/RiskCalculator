# calculadora_riesgos_completa.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io

st.set_page_config(layout="wide")

# MULTILENGUAJE
lang = st.sidebar.radio("🌐 Language / Idioma", ("Español", "English"))

# TRADUCCIONES
texts = {
    "Español": {
        "title": "🛡️ Calculadora de Riesgos (ASIS + Monte Carlo)",
        "add": "Agregar riesgo",
        "summary": "Resumen de Riesgo Agregado",
        "heatmap": "📊 Mapa de Calor de Riesgos",
        "pareto": "📈 Pareto - Riesgos Residuales",
        "matrix": "📋 Matriz Acumulativa de Riesgos",
        "download": "Descargar Excel"
    },
    "English": {
        "title": "🛡️ Risk Calculator (ASIS + Monte Carlo)",
        "add": "Add Risk",
        "summary": "Added Risk Summary",
        "heatmap": "📊 Risk Heatmap",
        "pareto": "📈 Pareto - Residual Risks",
        "matrix": "📋 Cumulative Risk Matrix",
        "download": "Download Excel"
    }
}

t = texts[lang]

st.title(t["title"])

# MATRICES Y PARÁMETROS

impact_weights = {
    "Humano": 0.25, "Operacional": 0.20, "Económico": 0.15,
    "Infraestructura": 0.12, "Tecnológico": 0.10, "Reputacional": 0.08,
    "Ambiental": 0.05, "Comercial": 0.03, "Social": 0.02
}

impact_levels = {
    "Insignificante (5)": 5,
    "Leve (10)": 10,
    "Moderado (30)": 30,
    "Grave (60)": 60,
    "Crítico (85)": 85
}

exposure_factors = {
    "Muy Baja (0.05) - Exposición extremadamente rara": 0.05,
    "Baja (0.15) - Ocasional (cada 10 años)": 0.15,
    "Moderada (0.30) - Algunas veces al año": 0.30,
    "Alta (0.55) - Mensual": 0.55,
    "Muy Alta (0.85) - Semanal": 0.85
}

probability_factors = {
    "Muy Baja (0.05) - En condiciones excepcionales": 0.05,
    "Baja (0.15) - Ha sucedido alguna vez": 0.15,
    "Moderada (0.30) - Podría ocurrir ocasionalmente": 0.30,
    "Alta (0.55) - Probable en ocasiones": 0.55,
    "Muy Alta (0.85) - Frecuente/inminente": 0.85
}

control_factors = {
    "Inefectiva (0%)": 0,
    "Limitada (0.1)": 0.1,
    "Baja (0.3)": 0.3,
    "Intermedia (0.5)": 0.5,
    "Alta (0.7)": 0.7,
    "Muy Alta (0.9)": 0.9,
    "Total (1.0)": 1.0
}

# VARIABLES GLOBALES
if "matriz_acum" not in st.session_state:
    st.session_state["matriz_acum"] = pd.DataFrame()

# ENTRADA DE RIESGO
st.subheader(t["add"])

evento = st.text_input("Descripción del Evento:")

impact_values = {}
for impacto, peso in impact_weights.items():
    seleccion = st.selectbox(f"Impacto {impacto}", options=list(impact_levels.keys()), key=impacto)
    impact_values[impacto] = impact_levels[seleccion]

impacto_total = sum(impact_values[k] * w for k, w in impact_weights.items())

exposicion = st.selectbox("Nivel de Exposición", list(exposure_factors.keys()))
probabilidad = st.selectbox("Nivel de Probabilidad", list(probability_factors.keys()))
controles = st.selectbox("Efectividad de Controles", list(control_factors.keys()))

Q = exposure_factors[exposicion] * probability_factors[probabilidad]
U = impacto_total
mitigacion = control_factors[controles]
riesgo_residual = Q * U * (1 - mitigacion)
indice_criticidad = riesgo_residual / 294

if st.button(t["add"]):
    nuevo = pd.DataFrame([{
        "Evento": evento,
        "Q": round(Q, 4),
        "U (Impacto)": U,
        "Mitigación": mitigacion,
        "Riesgo Residual": round(riesgo_residual, 2),
        "Índice Criticidad": round(indice_criticidad, 2)
    }])
    st.session_state["matriz_acum"] = pd.concat([st.session_state["matriz_acum"], nuevo], ignore_index=True)
    st.success("✅ Riesgo agregado exitosamente")

# VISUALIZACIONES
matriz_acum = st.session_state["matriz_acum"]

if not matriz_acum.empty:
    st.subheader(t["summary"])
    st.dataframe(matriz_acum, use_container_width=True)

    # MAPA DE CALOR
    st.subheader(t["heatmap"])
    matriz_heat = matriz_acum.pivot_table(index="Evento", values="Riesgo Residual", aggfunc="sum")
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(matriz_heat, annot=True, cmap="YlOrRd", ax=ax)
    st.pyplot(fig)

    # PARETO
    st.subheader(t["pareto"])
    pareto = matriz_acum.sort_values("Riesgo Residual", ascending=False)
    fig2 = px.bar(pareto, x="Evento", y="Riesgo Residual", title="Gráfico de Pareto", text_auto=True)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader(t["matrix"])
    st.dataframe(matriz_acum, use_container_width=True)

    # DESCARGA
    def to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Riesgos", index=False)
        return output.getvalue()

    excel_data = to_excel(matriz_acum)
    st.download_button(
        label=t["download"],
        data=excel_data,
        file_name="riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )



