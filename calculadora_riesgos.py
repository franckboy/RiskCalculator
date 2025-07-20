import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
import plotly.express as px

st.set_page_config(layout="wide", page_title="Calculadora de Riesgos")

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

colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]
cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Exposición", "Probabilidad", "Efectividad Control (%)",
        "Impacto", "Tipo Impacto",
        "Amenaza Inherente", "Amenaza Residual", "Riesgo Residual"
    ])

def clasificar_riesgo(valor):
    if valor <= 0.7:
        return "ACEPTABLE"
    elif valor <= 3.0:
        return "TOLERABLE"
    elif valor <= 7.0:
        return "INACEPTABLE"
    else:
        return "INADMISIBLE"

# Layout principal: Izquierda tablas y gráficos, derecha formulario y matriz
col_izq, col_der = st.columns([1.5, 3])

with col_izq:
    st.markdown("### Tablas de referencia")
    st.markdown("#### Efectividad de Controles")
    st.dataframe(tabla_efectividad.style.hide_index(), use_container_width=True)
    st.markdown("---")

    st.markdown("#### Factor de Exposición")
    st.dataframe(tabla_exposicion.style.hide_index(), use_container_width=True)
    st.markdown("---")

    st.markdown("#### Factor de Probabilidad")
    st.dataframe(tabla_probabilidad.style.hide_index(), use_container_width=True)
    st.markdown("---")

    st.markdown("#### Impacto / Severidad")
    st.dataframe(tabla_impacto.style.hide_index(), use_container_width=True)
    st.markdown("---")

    st.markdown("#### Índice de Criticidad")
    st.dataframe(tabla_criticidad.drop(columns="Color").style.hide_index(), use_container_width=True)
    st.markdown("---")

    st.markdown("#### Semáforo de colores (Leyenda)")
    st.markdown(
        """
        <ul>
            <li style='color:green; font-weight:bold;'>🟢 Verde: Aceptable (Hasta 0.7)</li>
            <li style='color:gold; font-weight:bold;'>🟡 Amarillo: Tolerable (> 0.7 hasta 3.0)</li>
            <li style='color:orange; font-weight:bold;'>🟠 Naranja: Inaceptable (> 3.0 hasta 7.0)</li>
            <li style='color:red; font-weight:bold;'>🔴 Rojo: Inadmisible (Más de 7)</li>
        </ul>
        """, unsafe_allow_html=True
    )

    if not st.session_state.riesgos.empty:
        riesgos = st.session_state.riesgos.copy()

        st.markdown("---")
        st.subheader("Gráfico interactivo: Riesgo Residual por Escenario")
        fig_bar = px.bar(
            riesgos,
            x="Riesgo Residual",
            y="Nombre Riesgo",
            orientation="h",
            color=riesgos["Riesgo Residual"].apply(clasificar_riesgo),
            color_discrete_map={
                "ACEPTABLE": "green",
                "TOLERABLE": "gold",
                "INACEPTABLE": "orange",
                "INADMISIBLE": "red"
            },
            title="Riesgo Residual por Escenario"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.subheader("Mapa de calor interactivo")
        matriz_calor = riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Efectividad Control (%)",
            values="Riesgo Residual",
            aggfunc=np.mean
        ).fillna(0).reset_index()

        fig_heat = px.imshow(
            matriz_calor.set_index("Tipo Impacto").values,
            labels=dict(x="Efectividad Control (%)", y="Tipo Impacto", color="Riesgo Residual"),
            x=matriz_calor.columns[1:].tolist(),
            y=matriz_calor["Tipo Impacto"],
            color_continuous_scale=["green", "yellow", "orange", "red"],
            aspect="auto",
            title="Mapa de calor de Riesgo Residual"
        )
        st.plotly_chart(fig_heat, use_container_width=True)

with col_der:
    st.title("Calculadora de Riesgos")

    editar_index = st.session_state.get("editar_index", None)

    # Filtro por Tipo de Impacto arriba formulario para mejorar UX
    tipos_impacto_unicos = st.session_state.riesgos["Tipo Impacto"].unique().tolist()
    filtro_impacto = st.multiselect(
        "Filtrar matriz acumulativa por Tipo de Impacto",
        options=["Humano", "Económico", "Operacional", "Ambiental", "Infraestructura",
                 "Tecnológico", "Reputacional", "Comercial", "Social"],
        default=tipos_impacto_unicos if tipos_impacto_unicos else None,
        help="Selecciona uno o más tipos para filtrar la tabla y gráficos."
    )

    if editar_index is not None:
        riesgo_editar = st.session_state.riesgos.loc[editar_index]
        nombre_riesgo = st.text_input("Nombre del riesgo", value=riesgo_editar["Nombre Riesgo"])
        descripcion = st.text_area("Descripción del riesgo", value=riesgo_editar["Descripción"], height=80)
        exposicion = riesgo_editar["Exposición"]
        probabilidad = riesgo_editar["Probabilidad"]
        efectividad = riesgo_editar["Efectividad Control (%)"]
        impacto = riesgo_editar["Impacto"]
        tipo_impacto = riesgo_editar["Tipo Impacto"]
    else:
        nombre_riesgo = st.text_input("Nombre del riesgo")
        descripcion = st.text_area("Descripción del riesgo", height=80)
        exposicion = st.selectbox(
            "Factor de Exposición",
            tabla_exposicion["Factor"],
            help="Selecciona el nivel de exposición según la tabla de referencia."
        )
        probabilidad = st.selectbox(
            "Factor de Probabilidad",
            tabla_probabilidad["Factor"],
            help="Selecciona el nivel de probabilidad según la tabla de referencia."
        )
        efectividad = st.slider("Efectividad del control (%)", 0, 100, 50, help="Porcentaje de reducción del riesgo.")
        impacto = st.slider("Impacto (1 a 5)", 1, 5, 3, help="Selecciona el nivel de impacto según la tabla.")
        tipo_impacto = st.selectbox(
            "Tipo de Impacto",
            ["Humano", "Económico", "Operacional", "Ambiental", "Infraestructura",
             "Tecnológico", "Reputacional", "Comercial", "Social"],
            help="Selecciona el tipo de impacto que mejor describe el riesgo."
        )

    efec_norm = efectividad / 100
    amenaza_inherente = round(exposicion * probabilidad, 4)
    amenaza_residual = round(amenaza_inherente * (1 - efec_norm), 4)
    riesgo_residual = round(amenaza_residual * impacto, 4)

    clasificacion = clasificar_riesgo(riesgo_residual)

    st.markdown("### Resultados del riesgo:")
    st.write(f"- Amenaza Inherente: {amenaza_inherente}")
    st.write(f"- Amenaza Residual: {amenaza_residual}")
    st.write(f"- Riesgo Residual: {riesgo_residual}")
    st.write(f"- Clasificación: **{clasificacion}**")

    col_add_edit = st.columns(2)
    with col_add_edit[0]:
        if editar_index is not None:
            if st.button("Guardar Cambios"):
                st.session_state.riesgos.loc[editar_index] = {
                    "Nombre Riesgo": nombre_riesgo.strip(),
                    "Descripción": descripcion.strip(),
                    "Exposición": exposicion,
                    "Probabilidad": probabilidad,
                    "Efectividad Control (%)": efectividad,
                    "Impacto": impacto,
                    "Tipo Impacto": tipo_impacto,
                    "Amenaza Inherente": amenaza_inherente,
                    "Amenaza Residual": amenaza_residual,
                    "Riesgo Residual": riesgo_residual
                }
                st.success("Riesgo actualizado.")
                st.session_state.editar_index = None
                st.experimental_rerun()
        else:
            if st.button("Agregar riesgo a la matriz") and nombre_riesgo.strip() != "":
                nuevo_riesgo = {
                    "Nombre Riesgo": nombre_riesgo.strip(),
                    "Descripción": descripcion.strip(),
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

    with col_add_edit[1]:
        if st.button("🔄 Limpiar matriz de riesgos"):
            st
