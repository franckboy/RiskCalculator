import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

# ---------- Tablas de referencia ----------
tabla_amenaza = pd.DataFrame({
    "Nivel": [1, 2, 3, 4, 5],
    "Clasificacion": ["Rara", "Poco Probable", "Posible", "Probable", "Casi Seguro"],
    "Rango": ["≤ 0.05", "0.06 – 0.15", "0.16 – 0.40", "0.41 – 0.70", "> 0.70"],
    "Factor": [0.04, 0.10, 0.25, 0.55, 0.85],
    "Definición de Nombre": [
        "Evento muy poco probable",
        "Posible en circunstancias poco comunes",
        "Puede ocurrir ocasionalmente",
        "Ocurre con frecuencia",
        "Ocurre casi siempre o siempre"
    ]
})

tabla_exposicion = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
    "Definición": [
        "Exposición extremadamente rara",
        "Exposición ocasional (cada 10 años)",
        "Exposición algunas veces al año",
        "Exposición mensual",
        "Exposición frecuente o semanal"
    ]
})

tabla_probabilidad = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
    "Descripción": [
        "En condiciones excepcionales",
        "Ha sucedido alguna vez",
        "Podría ocurrir ocasionalmente",
        "Probable en ocasiones",
        "Ocurre con frecuencia / inminente"
    ]
})

tipos_impacto = {
    "H": "Humano",
    "E": "Económico",
    "O": "Operacional",
    "A": "Ambiental",
    "I": "Infraestructura",
    "T": "Tecnológico",
    "R": "Reputacional",
    "C": "Comercial",
    "S": "Social"
}

# ---------- Inicialización ----------

st.title("Calculadora de Riesgos - Matriz Acumulativa con Mapa de Calor")

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Exposición", "Probabilidad", "Efectividad Control (%)", "Impacto", "Tipo Impacto",
        "Amenaza Inherente", "Amenaza Residual", "Riesgo Residual"
    ])

# ---------- Formulario para nuevo riesgo ----------

st.header("Agregar nuevo riesgo")

col1, col2, col3 = st.columns(3)

with col1:
    exposicion = st.selectbox("Factor de Exposición", tabla_exposicion["Factor"])
    probabilidad = st.selectbox("Factor de Probabilidad", tabla_probabilidad["Factor"])

with col2:
    efectividad = st.slider("Efectividad del control (%)", 0, 100, 50)
    impacto = st.slider("Impacto (1 a 5)", 1, 5, 3)

with col3:
    tipo_impacto = st.selectbox("Tipo de Impacto", list(tipos_impacto.keys()), format_func=lambda x: f"{x} - {tipos_impacto[x]}")

# ---------- Cálculos ----------

efec_norm = efectividad / 100
amenaza_inherente = round(exposicion * probabilidad, 4)
amenaza_residual = round(amenaza_inherente * (1 - efec_norm), 4)
riesgo_residual = round(amenaza_residual * impacto, 4)

st.markdown("### Resultados del nuevo riesgo:")
st.write(f"- Amenaza Inherente: {amenaza_inherente}")
st.write(f"- Amenaza Residual: {amenaza_residual}")
st.write(f"- Riesgo Residual: {riesgo_residual}")

# ---------- Botón para guardar riesgo ----------

if st.button("Agregar riesgo a la matriz"):
    nuevo_riesgo = {
        "Exposición": exposicion,
        "Probabilidad": probabilidad,
        "Efectividad Control (%)": efectividad,
        "Impacto": impacto,
        "Tipo Impacto": f"{tipo_impacto} - {tipos_impacto[tipo_impacto]}",
        "Amenaza Inherente": amenaza_inherente,
        "Amenaza Residual": amenaza_residual,
        "Riesgo Residual": riesgo_residual
    }
    st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
    st.success("Riesgo agregado.")

# ---------- Mostrar matriz acumulativa ----------

st.header("Matriz acumulativa de riesgos")

if not st.session_state.riesgos.empty:
    st.dataframe(st.session_state.riesgos)

    # Crear matriz para mapa de calor
    matriz_calor = st.session_state.riesgos.pivot_table(
        index="Tipo Impacto", columns="Efectividad Control (%)", values="Riesgo Residual", aggfunc=np.mean
    ).fillna(0)

    st.subheader("Mapa de calor de Riesgo Residual por Tipo de Impacto y Efectividad del Control")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(matriz_calor, annot=True, cmap="YlOrRd", ax=ax, fmt=".2f")
    ax.set_xlabel("Efectividad Control (%)")
    ax.set_ylabel("Tipo de Impacto")
    st.pyplot(fig)

    # Descargar Excel
    output = BytesIO()
   with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    st.session_state.riesgos.to_excel(writer

    st.download_button(
        label="Descargar matriz de riesgos en Excel",
        data=processed_data,
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Agrega riesgos para que se muestre la matriz acumulativa y el mapa de calor.")

