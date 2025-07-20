import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# -------- CONFIGURACIÓN INICIAL ----------
st.set_page_config(layout="wide", page_title="Evaluación de Riesgos", page_icon="⚠️")

st.title("🛡️ Evaluación de Riesgos")
st.markdown("Completa el formulario para evaluar el riesgo. Usa los valores adecuados para Impacto y Probabilidad.")

# ---------- FORMULARIO CENTRAL ----------------
with st.container():
    with st.form("formulario_riesgo", clear_on_submit=False):
        st.subheader("📋 Información del Riesgo")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del Riesgo", "")
        with col2:
            categoria = st.selectbox("Categoría", ["Seguridad", "Operativo", "Financiero", "Ambiental", "Otro"])

        descripcion = st.text_area("Descripción / Resumen", placeholder="Describe brevemente el riesgo...")

        st.subheader("⚙️ Parámetros")
        probabilidad = st.selectbox("Probabilidad", [0.05, 0.15, 0.30, 0.55, 0.85])
        impacto = st.selectbox("Impacto", [0.05, 0.15, 0.30, 0.55, 0.85])
        
        submit = st.form_submit_button("Calcular Riesgo")

# ---------- CÁLCULO DEL RIESGO Y CATEGORÍA ------------
if submit:
    riesgo = probabilidad * impacto
    if riesgo <= 0.7:
        categoria = "ACEPTABLE"
        color = "green"
    elif riesgo <= 3.0:
        categoria = "TOLERABLE"
        color = "yellow"
    elif riesgo <= 7.0:
        categoria = "INACEPTABLE"
        color = "orange"
    else:
        categoria = "INADMISIBLE"
        color = "red"

    st.markdown(f"### Resultado del Riesgo: **{riesgo:.2f}**")
    st.markdown(f"**Clasificación**: :{color}[{categoria}]")

# ---------- COLUMNAS CON TABLAS DE REFERENCIA ----------
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("📊 Factor de Exposición")
    datos_expo = {
        "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
        "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
        "Criterios": [
            "Exposición extremadamente rara",
            "Ocasional (cada 10 años)",
            "Algunas veces al año",
            "Mensual",
            "Frecuente o semanal"
        ]
    }
    st.dataframe(pd.DataFrame(datos_expo), use_container_width=True)

    st.subheader("📊 Factor de Probabilidad")
    datos_prob = {
        "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
        "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
        "Criterios": [
            "Condiciones excepcionales",
            "Ha sucedido alguna vez",
            "Podría ocurrir ocasionalmente",
            "Probable en ocasiones",
            "Ocurre con frecuencia / inminente"
        ]
    }
    st.dataframe(pd.DataFrame(datos_prob), use_container_width=True)

with col_der:
    st.subheader("📊 Impacto / Severidad")
    datos_impacto = {
        "Impacto": ["Bajo", "Moderado", "Alto", "Crítico"],
        "Valor": [0.05, 0.15, 0.30, 0.85],
        "Ejemplo": [
            "Sin consecuencias significativas",
            "Pérdidas leves",
            "Afecta una parte importante",
            "Pérdida total o fatalidad"
        ],
        "Frecuencia": ["Anual", "Semestral", "Mensual", "Frecuente"]
    }
    st.dataframe(pd.DataFrame(datos_impacto), use_container_width=True)

    st.subheader("📊 Efectividad de Controles")
    datos_controles = {
        "Rango": ["0%", "1-20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
        "Factor": [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.1],
        "Mitigación": ["Inefectiva", "Limitada", "Baja", "Intermedia", "Alta", "Muy Alta", "Total"],
        "Criterios": [
            "No reduce el riesgo",
            "Solo en condiciones ideales",
            "Mitiga riesgos menores",
            "Control estándar",
            "Reduce significativamente",
            "Robusto y bien implementado",
            "Elimina casi todo el riesgo"
        ]
    }
    st.dataframe(pd.DataFrame(datos_controles), use_container_width=True)

# ---------------- MAPA DE CALOR ---------------------
st.markdown("---")
st.subheader("📈 Mapa de Calor: Probabilidad vs Impacto")

# Datos para el mapa
valores = [0.05, 0.15, 0.30, 0.55, 0.85]
heatmap_data = np.zeros((len(valores), len(valores)))
colores = []

for i, p in enumerate(valores):
    for j, i_val in enumerate(valores):
        r = round(p * i_val, 2)
        heatmap_data[i, j] = r

# Colores según el riesgo
def obtener_color(valor):
    if valor <= 0.7:
        return "green"
    elif valor <= 3.0:
        return "yellow"
    elif valor <= 7.0:
        return "orange"
    else:
        return "red"

colores = np.vectorize(obtener_color)(heatmap_data)

# Gráfico
fig, ax = plt.subplots()
sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".2f",
    cmap=sns.color_palette(["green", "yellow", "orange", "red"]),
    xticklabels=valores,
    yticklabels=valores,
    cbar=False,
    ax=ax
)
ax.set_xlabel("Impacto")
ax.set_ylabel("Probabilidad")
st.pyplot(fig)

