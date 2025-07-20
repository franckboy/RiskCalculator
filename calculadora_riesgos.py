import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap

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

# ---------- Función para colorear índice de criticidad ----------
def color_criticidad(val):
    if pd.isna(val):
        return ""
    if val <= 2:
        return 'background-color: #00FF00; color: black'  # verde
    elif val <= 4:
        return 'background-color: #FFFF00; color: black'  # amarillo
    elif val <= 15:
        return 'background-color: #FFA500; color: black'  # naranja
    else:
        return 'background-color: #FF0000; color: white'  # rojo

# ---------- Inicialización ----------
st.title("Calculadora de Riesgos - Matriz Acumulativa con Mapa de Calor")

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Exposición", "Probabilidad", "Efectividad Control (%)",
        "Impacto", "Tipo Impacto", "Amenaza Inherente", "Amenaza Residual",
        "Margen Seguridad", "Riesgo Residual", "Indice Criticidad",
        "Factor Deliberacion", "Indice Criticidad Deliberado"
    ])

# ---------- Formulario para nuevo riesgo ----------
st.header("Agregar nuevo riesgo")

nombre_riesgo = st.text_input("Nombre del Riesgo")

col1, col2, col3 = st.columns(3)

with col1:
    exposicion = st.selectbox("Factor de Exposición", tabla_exposicion["Factor"])
    probabilidad = st.selectbox("Factor de Probabilidad", tabla_probabilidad["Factor"])

with col2:
    efectividad = st.slider("Efectividad del control (%)", 0, 100, 50)
    impacto = st.slider("Impacto (1 a 5)", 1, 5, 3)

with col3:
    tipo_impacto = st.selectbox(
        "Tipo de Impacto",
        list(tipos_impacto.keys()),
        format_func=lambda x: f"{x} - {tipos_impacto[x]}"
    )
    factor_deliberacion = st.number_input(
        "Factor de Deliberación (1 a 3)",
        min_value=1.0,
        max_value=3.0,
        value=1.4,
        step=0.1
    )

# ---------- Cálculos ----------
efec_norm = efectividad / 100
amenaza_inherente = round(exposicion * probabilidad, 4)

# Riesgo Residual Q
Q = round(amenaza_inherente * (1 - efec_norm) * exposicion * probabilidad, 4)  # según VBA

margen_seguridad = 0.25 * (1 - efec_norm)
S = round(Q * (1 + margen_seguridad), 4)

W = round(S * impacto, 4)

indice_criticidad = round(S * 100, 4)  # escala como en VBA
indice_criticidad_deliberado = round(indice_criticidad * factor_deliberacion, 4)

# Mostrar resultados
st.markdown("### Resultados del nuevo riesgo:")
st.write(f"- Amenaza Inherente: {amenaza_inherente}")
st.write(f"- Amenaza Residual (Q): {Q}")
st.write(f"- Margen de Seguridad (S): {S}")
st.write(f"- Riesgo Residual (W): {W}")
st.write(f"- Índice de Criticidad: {indice_criticidad}")
st.write(f"- Índice de Criticidad Deliberado: {indice_criticidad_deliberado}")

# ---------- Botón para guardar riesgo ----------
if st.button("Agregar riesgo a la matriz"):
    if not nombre_riesgo.strip():
        st.error("Por favor ingresa un nombre para el riesgo antes de agregarlo.")
    else:
        nuevo_riesgo = {
            "Nombre Riesgo": nombre_riesgo.strip(),
            "Exposición": exposicion,
            "Probabilidad": probabilidad,
            "Efectividad Control (%)": efectividad,
            "Impacto": impacto,
            "Tipo Impacto": f"{tipo_impacto} - {tipos_impacto[tipo_impacto]}",
            "Amenaza Inherente": amenaza_inherente,
            "Amenaza Residual": Q,
            "Margen Seguridad": S,
            "Riesgo Residual": W,
            "Indice Criticidad": indice_criticidad,
            "Factor Deliberacion": factor_deliberacion,
            "Indice Criticidad Deliberado": indice_criticidad_deliberado
        }
        st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
        st.success("Riesgo agregado.")

# ---------- Mostrar matriz acumulativa ----------
st.header("Matriz acumulativa de riesgos")

if not st.session_state.riesgos.empty:
    # Mostrar DataFrame con colores en Índices
    styled_df = st.session_state.riesgos.style.applymap(
        color_criticidad, subset=["Indice Criticidad", "Indice Criticidad Deliberado"]
    )
    st.dataframe(styled_df, use_container_width=True)

    # Crear colormap personalizado para heatmap
    colores = ["#00FF00", "#FFFF00", "#FFA500", "#FF0000"]
    custom_cmap = LinearSegmentedColormap.from_list("custom_criticidad", colores)

    # Pivot para matriz calor usando Riesgo Residual
    matriz_calor = st.session_state.riesgos.pivot_table(
        index="Tipo Impacto",
        columns="Efectividad Control (%)",
        values="Riesgo Residual",
        aggfunc=np.mean
    ).fillna(0)

    st.subheader("Mapa de calor de Riesgo Residual por Tipo de Impacto y Efectividad del Control")

    max_val = 20  # Ajusta según tus datos

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        matriz_calor,
        annot=True,
        cmap=custom_cmap,
        vmin=0,
        vmax=max_val,
        ax=ax,
        fmt=".2f",
        cbar_kws={'label': 'Riesgo Residual'}
    )
    ax.set_xlabel("Efectividad Control (%)")
    ax.set_ylabel("Tipo de Impacto")
    st.pyplot(fig)

    # Descargar Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        st.session_state.riesgos.to_excel(writer, index=False, sheet_name="Riesgos")
    processed_data = output.getvalue()

    st.download_button(
        label="Descargar matriz de riesgos en Excel",
        data=processed_data,
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Agrega riesgos para que se muestre la matriz acumulativa y el mapa de calor.")
