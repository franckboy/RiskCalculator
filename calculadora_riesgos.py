import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

# --- Tablas fijas para referencia (ejemplo, actualiza con tus tablas completas) ---
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
        "≤ 4",
        "≤ 15",
        "> 15",
        "Más de 15"
    ],
    "Color": ["Verde", "Amarillo", "Naranja", "Rojo"]
})

# Colores para mapa de calor y leyendas
colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]  # Verde, Amarillo, Naranja, Rojo
cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

# Función para mostrar tablas fijas con tooltips y columnas seleccionadas
def mostrar_tabla_con_tooltip(df, cols_a_mostrar, tooltip_col, titulo):
    st.markdown(f"**{titulo}**")
    df_to_show = df[cols_a_mostrar].copy()
    gb = GridOptionsBuilder.from_dataframe(df_to_show)
    gb.configure_default_column(
        editable=False,
        filter=False,
        sortable=False,
        resizable=True,
        cellStyle={"textAlign": "center", "verticalAlign": "middle", "white-space": "normal"}
    )
    gb.configure_column(cols_a_mostrar[0], tooltipField=tooltip_col)
    gb.configure_grid_options(domLayout='autoHeight')
    gridOptions = gb.build()
    AgGrid(df_to_show, gridOptions=gridOptions, fit_columns_on_grid_load=True)

# Inicializar estado para riesgos
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Tipo Impacto",
        "Amenaza Inherente", "Amenaza Residual", "Riesgo Residual"
    ])

# Layout columnas
col_izq, col_centro, col_der = st.columns([1.3, 2.5, 1.3])

with col_izq:
    mostrar_tabla_con_tooltip(
        tabla_efectividad,
        cols_a_mostrar=["Rango", "Factor", "Mitigacion"],
        tooltip_col="Descripcion",
        titulo="Efectividad de Controles"
    )
    mostrar_tabla_con_tooltip(
        tabla_exposicion,
        cols_a_mostrar=["Factor", "Nivel"],
        tooltip_col="Definición de Criterios",
        titulo="Factor de Exposición"
    )
    mostrar_tabla_con_tooltip(
        tabla_probabilidad,
        cols_a_mostrar=["Factor", "Nivel"],
        tooltip_col="Descripcion",
        titulo="Factor de Probabilidad"
    )
    mostrar_tabla_con_tooltip(
        tabla_impacto,
        cols_a_mostrar=["Nivel", "Valor"],
        tooltip_col="Definición de Criterios",
        titulo="Impacto / Severidad"
    )
    mostrar_tabla_con_tooltip(
        tabla_criticidad.drop(columns=["Color"]),
        cols_a_mostrar=["Límite Superior", "Clasificación"],
        tooltip_col="Clasificación",
        titulo="Índice de Criticidad"
    )
    # Leyenda de colores (sin iconos)
    st.markdown("### Leyenda de Colores de Criticidad")
    st.markdown(
        """
        <ul>
            <li style='color:#008000; font-weight:bold;'>Verde: ACEPTABLE (≤ 4)</li>
            <li style='color:#FFD700; font-weight:bold;'>Amarillo: TOLERABLE (≤ 15)</li>
            <li style='color:#FF8C00; font-weight:bold;'>Naranja: INACEPTABLE (> 15)</li>
            <li style='color:#FF0000; font-weight:bold;'>Rojo: INADMISIBLE (Más de 15)</li>
        </ul>
        """,
        unsafe_allow_html=True
    )

with col_centro:
    st.title("Calculadora de Riesgos")

    nombre_riesgo = st.text_input("Nombre del riesgo")
    descripcion = st.text_area("Descripción del riesgo")

    exposicion = st.selectbox("Factor de Exposición", tabla_exposicion["Factor"])
    probabilidad = st.selectbox("Factor de Probabilidad", tabla_probabilidad["Factor"])
    amenaza_deliberada = st.selectbox("Amenaza Deliberada (1 - 3)", [1, 2, 3], index=0)

    efectividad = st.slider("Efectividad del control (%)", 0, 100, 50)
    impacto = st.slider("Impacto (1 a 5)", 1, 5, 3)
    tipo_impacto = st.selectbox(
        "Tipo de Impacto",
        ["Humano", "Económico", "Operacional", "Ambiental", "Infraestructura", "Tecnológico", "Reputacional", "Comercial", "Social"]
    )

    efec_norm = efectividad / 100
    amenaza_inherente = round(exposicion * probabilidad * amenaza_deliberada, 4)
    amenaza_residual = round(amenaza_inherente * (1 - efec_norm), 4)
    riesgo_residual = round(amenaza_residual * impacto, 4)

    st.markdown("### Resultados del nuevo riesgo:")
    st.write(f"- Amenaza Inherente: {amenaza_inherente}")
    st.write(f"- Amenaza Residual: {amenaza_residual}")
    st.write(f"- Riesgo Residual: {riesgo_residual}")

    if st.button("Agregar riesgo a la matriz") and nombre_riesgo.strip() != "":
        nuevo_riesgo = {
            "Nombre Riesgo": nombre_riesgo.strip(),
            "Descripción": descripcion.strip(),
            "Exposición": exposicion,
            "Probabilidad": probabilidad,
            "Amenaza Deliberada": amenaza_deliberada,
            "Efectividad Control (%)": efectividad,
            "Impacto": impacto,
            "Tipo Impacto": tipo_impacto,
            "Amenaza Inherente": amenaza_inherente,
            "Amenaza Residual": amenaza_residual,
            "Riesgo Residual": riesgo_residual
        }
        st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
        st.success("Riesgo agregado.")

with col_der:
    st.markdown("## Mapas de Calor")

    if not st.session_state.riesgos.empty:
        matriz_calor = st.session_state.riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Efectividad Control (%)",
            values="Riesgo Residual",
            aggfunc=np.mean
        ).fillna(0)

        fig, ax = plt.subplots(figsize=(8, 6))
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
    else:
        st.info("Agrega riesgos para mostrar el mapa de calor.")

# Función para mostrar matriz acumulativa con AgGrid y scroll
def mostrar_matriz_acumulativa(df_riesgos):
    st.markdown("## Matriz Acumulativa de Riesgos")

    gb = GridOptionsBuilder.from_dataframe(df_riesgos)
    gb.configure_default_column(
        editable=False,
        filter=True,
        sortable=True,
        resizable=True,
        cellStyle={"textAlign": "center", "verticalAlign": "middle", "white-space": "normal"}
    )
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()

    AgGrid(
        df_riesgos,
        gridOptions=gridOptions,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True,
        theme='balham',
        height=400,
        fit_columns_on_grid_load=True
    )

st.markdown("---")
if not st.session_state.riesgos.empty:
    mostrar_matriz_acumulativa(st.session_state.riesgos)
else:
    st.info("Agrega riesgos para que se muestre la matriz acumulativa.")

