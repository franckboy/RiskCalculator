import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Calculadora de Riesgos ASIS")

# Tablas fijas

tabla_efectividad = pd.DataFrame({
    "Efectividad Control": ["Alta", "Media", "Baja"],
    "Valor": [0.2, 0.5, 1.0],
    "Descripción": [
        "Controles completamente efectivos",
        "Controles moderadamente efectivos",
        "Controles poco efectivos o inexistentes"
    ]
})

tabla_exposicion = pd.DataFrame({
    "Exposición": ["Muy Baja", "Baja", "Media", "Alta"],
    "Valor": [0.1, 0.25, 0.5, 1.0],
    "Frecuencia": [
        "Menos de una vez al año",
        "Una vez al año",
        "Una vez al mes",
        "Más de una vez al mes"
    ]
})

tabla_probabilidad = pd.DataFrame({
    "Probabilidad": ["Remota", "Posible", "Probable", "Frecuente"],
    "Valor": [0.1, 0.3, 0.6, 0.9],
    "Descripción": [
        "Muy baja probabilidad",
        "Probabilidad media",
        "Alta probabilidad",
        "Muy alta probabilidad"
    ]
})

tabla_impacto = pd.DataFrame({
    "Impacto": ["Leve", "Moderado", "Severo", "Crítico"],
    "Valor": [1, 3, 7, 10],
    "Descripción": [
        "Impacto mínimo",
        "Impacto medio",
        "Impacto grave",
        "Impacto muy grave o pérdida total"
    ]
})

tabla_criticidad = pd.DataFrame({
    "Clasificación": ["Baja", "Media", "Alta", "Extrema"],
    "Rango": ["0-5", "6-15", "16-30", ">30"],
    "Color": ["#A9D18E", "#FFD966", "#F4B084", "#C00000"]
})

tabla_semaforo = pd.DataFrame({
    "Nivel": ["Bajo", "Medio", "Alto", "Extremo"],
    "Color": ["🟩", "🟨", "🟧", "🟥"]
})

def mostrar_tabla_aggrid(df, titulo, height=200):
    st.markdown(f"**{titulo}**")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_grid_options(domLayout='autoHeight')
    gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True, editable=False)
    gb.configure_pagination(enabled=False)
    gridOptions = gb.build()
    AgGrid(df.reset_index(drop=True), gridOptions=gridOptions, fit_columns_on_grid_load=True, height=height)
    st.markdown("---")

def clasificar_criticidad(valor):
    for i, row in tabla_criticidad.iterrows():
        limites = row["Rango"].split("-")
        if len(limites) == 2:
            min_val = float(limites[0])
            max_val = float(limites[1])
            if min_val <= valor <= max_val:
                return row["Clasificación"], row["Color"]
        else:  # rango >30
            if valor > 30:
                return row["Clasificación"], row["Color"]
    return "No Clasificado", "#000000"

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Efectividad Control", "Valor Efectividad",
        "Exposición", "Valor Exposición", "Probabilidad", "Valor Probabilidad",
        "Amenaza Deliberada", "Impacto", "Valor Impacto",
        "Riesgo Residual"
    ])

# Layout columnas
col_izq, col_centro, col_der = st.columns([1.2, 2.0, 1.8])

with col_izq:
    mostrar_tabla_aggrid(tabla_efectividad, "Efectividad de Controles")
    mostrar_tabla_aggrid(tabla_exposicion, "Factor de Exposición")
    mostrar_tabla_aggrid(tabla_probabilidad, "Factor de Probabilidad")
    mostrar_tabla_aggrid(tabla_impacto, "Impacto / Severidad")
    mostrar_tabla_aggrid(tabla_criticidad.drop(columns=["Color"]), "Índice de Criticidad")
    mostrar_tabla_aggrid(tabla_semaforo, "Semáforo (Leyenda)")

with col_centro:
    st.title("🛡️ Calculadora de Riesgos ASIS")
    st.subheader("Ingresar nuevo riesgo")

    nombre = st.text_input("Nombre del riesgo")
    descripcion = st.text_area("Descripción del riesgo")

    efec = st.selectbox("Efectividad del control", options=tabla_efectividad["Efectividad Control"])
    valor_efec = tabla_efectividad.loc[tabla_efectividad["Efectividad Control"]==efec, "Valor"].values[0]

    expo = st.selectbox("Exposición", options=tabla_exposicion["Exposición"])
    valor_expo = tabla_exposicion.loc[tabla_exposicion["Exposición"]==expo, "Valor"].values[0]

    prob = st.selectbox("Probabilidad", options=tabla_probabilidad["Probabilidad"])
    valor_prob = tabla_probabilidad.loc[tabla_probabilidad["Probabilidad"]==prob, "Valor"].values[0]

    amenaza_delib = st.select_slider(
        "Amenaza deliberada (intencionalidad del riesgo)",
        options=[1, 2, 3],
        value=1,
        help="1 = baja intención, 3 = alta intención"
    )

    impact = st.selectbox("Impacto / Severidad", options=tabla_impacto["Impacto"])
    valor_impact = tabla_impacto.loc[tabla_impacto["Impacto"]==impact, "Valor"].values[0]

    riesgo_residual = round(
        (1 - valor_efec) * valor_expo * valor_prob * valor_impact * amenaza_delib,
        4
    )

    st.markdown(f"**Riesgo Residual calculado:** {riesgo_residual}")

    if st.button("Agregar riesgo") and nombre.strip() != "":
        nuevo = {
            "Nombre Riesgo": nombre.strip(),
            "Descripción": descripcion.strip(),
            "Efectividad Control": efec,
            "Valor Efectividad": valor_efec,
            "Exposición": expo,
            "Valor Exposición": valor_expo,
            "Probabilidad": prob,
            "Valor Probabilidad": valor_prob,
            "Amenaza Deliberada": amenaza_delib,
            "Impacto": impact,
            "Valor Impacto": valor_impact,
            "Riesgo Residual": riesgo_residual
        }
        st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo])], ignore_index=True)
        st.success("Riesgo agregado.")

    st.markdown("---")
    st.subheader("Matriz Acumulativa de Riesgos")

    if not st.session_state.riesgos.empty:
        cols_esperadas = [
            "Nombre Riesgo", "Descripción", "Efectividad Control",
            "Exposición", "Probabilidad", "Amenaza Deliberada",
            "Impacto", "Riesgo Residual"
        ]
        cols_presentes = [c for c in cols_esperadas if c in st.session_state.riesgos.columns]

        gb = GridOptionsBuilder.from_dataframe(st.session_state.riesgos[cols_presentes])
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
        gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True)
        gridOptions = gb.build()
        AgGrid(st.session_state.riesgos[cols_presentes], gridOptions=gridOptions, fit_columns_on_grid_load=True, height=300)

        impacto_acumulado = st.session_state.riesgos["Riesgo Residual"].sum()
        indice_criticidad_global = round((impacto_acumulado / 294) * 100, 2)
        clasificacion_global, color_global = clasificar_criticidad(indice_criticidad_global)

        st.markdown(f"**Impacto acumulado:** {impacto_acumulado:.4f}")
        st.markdown(f"**Índice global de criticidad ASIS:** <span style='color:{color_global}; font-weight:bold;'>{indice_criticidad_global}% - {clasificacion_global}</span>", unsafe_allow_html=True)

    else:
        st.info("Agrega riesgos para ver la matriz acumulativa y el índice global.")

with col_der:
    st.subheader("Mapa de calor (Probabilidad × Impacto)")
    if not st.session_state.riesgos.empty:
        probs = sorted(st.session_state.riesgos["Valor Probabilidad"].unique())
        impacts = sorted(st.session_state.riesgos["Valor Impacto"].unique())

        heatmap_data = pd.DataFrame(0, index=probs, columns=impacts, dtype=float)
        for _, fila in st.session_state.riesgos.iterrows():
            heatmap_data.loc[fila["Valor Probabilidad"], fila["Valor Impacto"]] += fila["Valor Probabilidad"] * fila["Valor Impacto"]

        plt.figure(figsize=(8,5))
        sns.heatmap(
            heatmap_data,
            annot=True,
            fmt=".2f",
            cmap="RdYlGn_r",
            cbar_kws={"label": "Probabilidad × Impacto"},
            linewidths=0.5,
            linecolor="gray"
        )
        plt.title("Mapa de calor Probabilidad x Impacto")
        plt.xlabel("Impacto")
        plt.ylabel("Probabilidad")
        st.pyplot(plt.gcf())
    else:
        st.info("Agrega riesgos para ver el mapa de calor.")
