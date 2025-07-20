import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap

st.set_page_config(layout="wide")

# --- Tablas fijas para referencia ---
tabla_impacto = pd.DataFrame({
    "Nivel": [1, 2, 3, 4, 5],
    "Valor": [5, 10, 30, 60, 85],
    "Clasificacion": ["Insignificante", "Leve", "Moderado", "Grave", "Critico"],
    "Definición de Criterios": [
        "No afecta significativamente",
        "Afectación menor",
        "Afectación parcial y temporal",
        "Afectación significativa",
        "Impacto serio o pérdida total"
    ]
})

tabla_amenaza_inherente = pd.DataFrame({
    "Nivel": [1, 2, 3, 4, 5],
    "Clasificacion": ["Rara", "Poco Probable", "Posible", "Probable", "Casi seguro"],
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
    "Definición de Criterios": [
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
    "Descripcion": [
        "En condiciones excepcionales",
        "Ha sucedido alguna vez",
        "Podría ocurrir ocasionalmente",
        "Probable en ocasiones",
        "Ocurre con frecuencia / inminente"
    ]
})

tabla_efectividad = pd.DataFrame({
    "Rango": ["0%", "1 - 20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
    "Factor": [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.1],
    "Mitigacion": ["Inefectiva", "Limitada", "Baja", "Intermedia", "Alta", "Muy alta", "Total"],
    "Descripcion": [
        "No reduce el riesgo",
        "Reduce solo en condiciones ideales",
        "Mitiga riesgos menores.",
        "Control estándar con limitaciones.",
        "Reduce significativamente el riesgo",
        "Control robusto y bien implementado.",
        "Elimina casi todo el riesgo"
    ]
})

tabla_criticidad = pd.DataFrame({
    "Límite Superior": [0.7, 3.0, 7.0, float('inf')],
    "Clasificación": ["ACEPTABLE", "TOLERABLE", "INACEPTABLE", "INADMISIBLE"],
    "Rango Aceptabilidad": [
        "Hasta 0.7",
        "> 0.7 hasta 3.0",
        "> 3.0 hasta 7.0",
        "Más de 7"
    ],
    "Color": ["Verde", "Amarillo", "Naranja", "Rojo"]
})

def mostrar_criticidad():
    st.markdown("### Índice de Criticidad y Aceptabilidad")
    st.dataframe(tabla_criticidad.drop(columns="Color"), use_container_width=True)
    st.markdown("**Leyenda de colores:**")
    st.markdown(
        """
        <ul>
            <li style='color:green;'>Verde: Aceptable (Hasta 0.7)</li>
            <li style='color:gold;'>Amarillo: Tolerable (> 0.7 hasta 3.0)</li>
            <li style='color:orange;'>Naranja: Inaceptable (> 3.0 hasta 7.0)</li>
            <li style='color:red;'>Rojo: Inadmisible (Más de 7)</li>
        </ul>
        """, unsafe_allow_html=True)

colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]
cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Exposición", "Probabilidad", "Efectividad Control (%)",
        "Impacto", "Tipo Impacto",
        "Amenaza Inherente", "Amenaza Residual", "Riesgo Residual"
    ])

col_izq, col_central, col_der = st.columns([1.2, 2.5, 1.2])

with col_izq:
    st.markdown("### Matriz Impacto / Severidad")
    st.dataframe(tabla_impacto, use_container_width=True)
    st.markdown("---")

    st.markdown("### Amenaza Inherente")
    st.dataframe(tabla_amenaza_inherente, use_container_width=True)
    st.markdown("---")

    st.markdown("### Factor de Exposición")
    st.dataframe(tabla_exposicion, use_container_width=True)
    st.markdown("---")

    st.markdown("### Factor de Probabilidad")
    st.dataframe(tabla_probabilidad, use_container_width=True)
    st.markdown("---")

    st.markdown("### Efectividad de Controles")
    st.dataframe(tabla_efectividad, use_container_width=True)
    st.markdown("---")

    mostrar_criticidad()

with col_central:
    st.title("Calculadora de Riesgos")
    st.subheader("Descripción del Riesgo")
    descripcion = st.text_area("Describe el riesgo brevemente", "")

    nombre_riesgo = st.text_input("Nombre del riesgo")

    exposicion_nivel = st.selectbox(
        "Nivel de Exposición",
        options=tabla_exposicion.index,
        format_func=lambda i: f"{tabla_exposicion.iloc[i]['Nivel']} ({tabla_exposicion.iloc[i]['Factor']})"
    )
    exposicion = tabla_exposicion.iloc[exposicion_nivel]['Factor']

    probabilidad_nivel = st.selectbox(
        "Nivel de Probabilidad",
        options=tabla_probabilidad.index,
        format_func=lambda i: f"{tabla_probabilidad.iloc[i]['Nivel']} ({tabla_probabilidad.iloc[i]['Factor']})"
    )
    probabilidad = tabla_probabilidad.iloc[probabilidad_nivel]['Factor']

    efectividad = st.slider("Efectividad del control (%)", 0, 100, 50)

    impacto_nivel = st.selectbox(
        "Nivel de Impacto",
        options=tabla_impacto.index,
        format_func=lambda i: f"{tabla_impacto.iloc[i]['Clasificacion']} ({tabla_impacto.iloc[i]['Valor']})"
    )
    impacto = tabla_impacto.iloc[impacto_nivel]['Valor']

    tipo_impacto = st.selectbox(
        "Tipo de Impacto",
        ["Humano", "Económico", "Operacional", "Ambiental", "Infraestructura", "Tecnológico", "Reputacional", "Comercial", "Social"]
    )

    efec_norm = efectividad / 100
    amenaza_inherente = round(exposicion * probabilidad, 4)
    amenaza_residual = round(amenaza_inherente * (1 - efec_norm), 4)
    riesgo_residual = round(amenaza_residual * impacto, 4)

    def clasificar_riesgo(valor):
        if valor <= 0.7:
            return "ACEPTABLE"
        elif valor <= 3.0:
            return "TOLERABLE"
        elif valor <= 7.0:
            return "INACEPTABLE"
        else:
            return "INADMISIBLE"

    clasificacion = clasificar_riesgo(riesgo_residual)

    st.markdown("### Resultados del nuevo riesgo:")
    st.write(f"- Amenaza Inherente: {amenaza_inherente}")
    st.write(f"- Amenaza Residual: {amenaza_residual}")
    st.write(f"- Riesgo Residual: {riesgo_residual}")
    st.write(f"- Clasificación: **{clasificacion}**")

    if st.button("Agregar riesgo a la matriz") and nombre_riesgo.strip() != "":
        nuevo_riesgo = {
            "Nombre Riesgo": nombre_riesgo.strip(),
            "Exposición": exposicion,
            "Probabilidad": probabilidad,
            "Efectividad Control (%)": efectividad,
            "Impacto": impacto,
            "Tipo Impacto": tipo_impacto,
            "Amenaza Inherente": amenaza_inherente,
            "Amenaza Residual": amenaza_residual,
            "Riesgo Residual": riesgo_residual
        }
        st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
        st.success("Riesgo agregado.")

    if st.button("🔄 Limpiar matriz de riesgos"):
        st.session_state.riesgos = pd.DataFrame(columns=st.session_state.riesgos.columns)
        st.warning("Matriz de riesgos reiniciada.")

with col_der:
    st.header("Matriz acumulativa de riesgos")

    if not st.session_state.riesgos.empty:
        riesgos = st.session_state.riesgos.copy()
        riesgos["Clasificación"] = riesgos["Riesgo Residual"].apply(clasificar_riesgo)

        st.dataframe(riesgos)

        matriz_calor = riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Efectividad Control (%)",
            values="Riesgo Residual",
            aggfunc=np.mean
        ).fillna(0)

        st.subheader("Mapa de calor de Riesgo Residual por Tipo de Impacto y Efectividad del Control")

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(
            matriz_calor,
            annot=True,
            fmt=".2f",
            cmap=cmap,
            cbar_kws={"label": "Riesgo Residual"}
        )
        ax.set_xlabel("Efectividad Control (%)")
        ax.set_ylabel("Tipo de Impacto")
        st.pyplot(fig)

        st.subheader("Comparación de Riesgo Residual por Escenario")
        fig_bar, ax_bar = plt.subplots()
        riesgos.plot(
            x="Nombre Riesgo", y="Riesgo Residual", kind="barh",
            ax=ax_bar, color="#1f77b4", legend=False
        )
        ax_bar.set_xlabel("Riesgo Residual")
        ax_bar.set_ylabel("Escenario")
        st.pyplot(fig_bar)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            riesgos.to_excel(writer, index=False, sheet_name="Riesgos")
        processed_data = output.getvalue()

        st.download_button(
            label="Descargar matriz de riesgos en Excel",
            data=processed_data,
            file_name="matriz_riesgos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Agrega riesgos para que se muestre la matriz acumulativa y el mapa de calor.")
