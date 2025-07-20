import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

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
    "Límite Superior": [2, 4, 15, float('inf')],
    "Clasificación": ["ACEPTABLE", "TOLERABLE", "INACEPTABLE", "INADMISIBLE"],
    "Rango Aceptabilidad": [
        "Hasta 0.7",
        "> 0.7 hasta 3.0",
        "> 3.0 hasta 7.0",
        "Más de 7"
    ],
    "Color": ["Verde", "Amarillo", "Naranja", "Rojo"]
})

# --- Función para mostrar tabla de criticidad con leyenda colores ---
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

# --- Función para asignar color basado en riesgo residual (índice criticidad) ---
from matplotlib.colors import LinearSegmentedColormap

def riesgo_a_color(val):
    """Convierte valor riesgo en color: verde, amarillo, naranja, rojo con degradados"""
    if val <= 0.7:
        # verde
        return "#008000"  # verde oscuro
    elif val <= 3:
        return "#FFD700"  # amarillo dorado
    elif val <= 7:
        return "#FF8C00"  # naranja oscuro
    else:
        return "#FF0000"  # rojo

# Para seaborn heatmap: definimos paleta personalizada con puntos clave
colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]
cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

# --- Inicialización datos de riesgos ---
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Exposición", "Probabilidad", "Efectividad Control (%)",
        "Impacto", "Tipo Impacto",
        "Amenaza Inherente", "Amenaza Residual", "Riesgo Residual"
    ])

# --- Layout con columnas ---
col_izq, col_der = st.columns([1, 3])

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

with col_der:
    st.title("Calculadora de Riesgos - Matriz Acumulativa con Mapa de Calor")

    # Formulario para nuevo riesgo
    st.header("Agregar nuevo riesgo")

    nombre_riesgo = st.text_input("Nombre del riesgo")
    exposicion = st.selectbox("Factor de Exposición", tabla_exposicion["Factor"])
    probabilidad = st.selectbox("Factor de Probabilidad", tabla_probabilidad["Factor"])
    efectividad = st.slider("Efectividad del control (%)", 0, 100, 50)
    impacto = st.slider("Impacto (1 a 5)", 1, 5, 3)
    tipo_impacto = st.selectbox(
        "Tipo de Impacto",
        ["Humano", "Económico", "Operacional", "Ambiental", "Infraestructura", "Tecnológico", "Reputacional", "Comercial", "Social"]
    )

    # Cálculos
    efec_norm = efectividad / 100
    amenaza_inherente = round(exposicion * probabilidad, 4)
    amenaza_residual = round(amenaza_inherente * (1 - efec_norm), 4)
    riesgo_residual = round(amenaza_residual * impacto, 4)

    st.markdown("### Resultados del nuevo riesgo:")
    st.write(f"- Amenaza Inherente: {amenaza_inherente}")
    st.write(f"- Amenaza Residual: {amenaza_residual}")
    st.write(f"- Riesgo Residual: {riesgo_residual}")

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

    # Mostrar matriz acumulativa y mapa de calor si hay datos
    st.header("Matriz acumulativa de riesgos")

    if not st.session_state.riesgos.empty:
        st.dataframe(st.session_state.riesgos)

        # Crear tabla pivote para heatmap: filas=Tipo Impacto, columnas=Efectividad Control (%), valores= promedio Riesgo Residual
        matriz_calor = st.session_state.riesgos.pivot_table(
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

        # Descargar Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            st.session_state.riesgos.to_excel(writer, index=False, sheet_name="Riesgos")
            writer.save()
            processed_data = output.getvalue()

        st.download_button(
            label="Descargar matriz de riesgos en Excel",
            data=processed_data,
            file_name="matriz_riesgos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Agrega riesgos para que se muestre la matriz acumulativa y el mapa de calor.")
