import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO

st.set_page_config(layout="wide")

# --- CSS personalizado ---
st.markdown("""
<style>
    div.stButton > button {
        background-color: #28a745;
        color: white;
        font-weight: bold;
        height: 40px;
        width: 100%;
        border-radius: 5px;
        border: none;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #218838;
        cursor: pointer;
    }
    div.stSelectbox > div[data-baseweb="select"] {
        width: 100% !important;
        font-size: 16px !important;
    }
    textarea {
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Tablas base ---

tabla_tipo_impacto = pd.DataFrame({
    "Código": ["H", "O", "E", "I", "T", "R", "A", "C", "S"],
    "Tipo de Impacto": [
        "Humano (H)", "Operacional (O)", "Económico (E)", "Infraestructura (I)",
        "Tecnológico (T)", "Reputacional (R)", "Ambiental (A)", "Comercial (C)", "Social (S)"
    ],
    "Ponderación": [25, 20, 15, 12, 10, 8, 5, 3, 2],
    "Explicación ASIS": [
        "Máxima prioridad: Protección de empleados, visitantes y stakeholders físicos (ASIS enfatiza la seguridad personal).",
        "Continuidad del negocio: Interrupciones críticas en procesos (ORM.1 exige planes de recuperación).",
        "Pérdidas financieras directas: Robos, fraudes, parálisis de ingresos (impacto en sostenibilidad).",
        "Activos físicos: Daño a instalaciones, equipos o cadenas de suministro (ASIS prioriza protección física).",
        "Ciberseguridad y datos: Hackeos, fallos de sistemas (ASIS lo vincula a riesgos operacionales).",
        "Imagen pública: Crisis por incidentes de seguridad o ética (difícil de cuantificar, pero crítico).",
        "Solo relevante si aplica: Derrames, contaminación (mayor peso en industrias reguladas).",
        "Relaciones con clientes: Pérdida de contratos o confianza (menos urgente que otros).",
        "Impacto comunitario: Solo crítico en sectores con alta interacción social (ej. minería)."
    ]
})

factor_exposicion = pd.DataFrame({
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

factor_probabilidad = pd.DataFrame({
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

criticidad_límites = [
    (0, 0.7, "ACEPTABLE", "#008000"),
    (0.7, 3, "TOLERABLE", "#FFD700"),
    (3, 7, "INACEPTABLE", "#FF8C00"),
    (7, float("inf"), "INADMISIBLE", "#FF0000")
]

textos = {
    "es": {
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion_riesgo": "Descripción del riesgo",
        "tipo_impacto": "Tipo de impacto",
        "justificacion": "Explicación según ASIS",
        "factor_exposicion": "Factor de exposición",
        "factor_probabilidad": "Factor de probabilidad",
        "amenaza_deliberada": "Amenaza deliberada",
        "amenaza_deliberada_opciones": {1: "No", 2: "Sí baja", 3: "Sí alta"},
        "efectividad_control": "Efectividad del control (%)",
        "impacto": "Impacto",
        "agregar_riesgo": "Agregar riesgo",
        "exito_agregar": "Riesgo agregado exitosamente",
        "resultados": "Resultados",
        "amenaza_inherente": "Amenaza Inherente",
        "amenaza_residual": "Amenaza Residual",
        "amenaza_residual_ajustada": "Amenaza Residual Ajustada",
        "riesgo_residual": "Riesgo Residual",
        "clasificacion": "Clasificación",
        "mapa_calor_titulo": "Mapa de Calor de Riesgos",
        "pareto_titulo": "Pareto - Riesgos Residuales",
        "matriz_acumulativa_titulo": "Matriz Acumulativa de Riesgos",
        "descargar_excel": "Descargar matriz en Excel",
        "info_agrega_riesgos": "Agrega riesgos para visualizar los gráficos.",
        "info_agrega_riesgos_matriz": "Agrega riesgos para mostrar la matriz acumulativa."
    },
    "en": {
        "nombre_riesgo": "Risk Name",
        "descripcion_riesgo": "Risk Description",
        "tipo_impacto": "Impact Type",
        "justificacion": "Explanation according to ASIS",
        "factor_exposicion": "Exposure Factor",
        "factor_probabilidad": "Probability Factor",
        "amenaza_deliberada": "Deliberate Threat",
        "amenaza_deliberada_opciones": {1: "No", 2: "Low", 3: "High"},
        "efectividad_control": "Control Effectiveness (%)",
        "impacto": "Impact",
        "agregar_riesgo": "Add Risk",
        "exito_agregar": "Risk added successfully",
        "resultados": "Results",
        "amenaza_inherente": "Inherent Threat",
        "amenaza_residual": "Residual Threat",
        "amenaza_residual_ajustada": "Adjusted Residual Threat",
        "riesgo_residual": "Residual Risk",
        "clasificacion": "Classification",
        "mapa_calor_titulo": "Risk Heatmap",
        "pareto_titulo": "Pareto - Residual Risks",
        "matriz_acumulativa_titulo": "Accumulated Risk Matrix",
        "descargar_excel": "Download matrix as Excel",
        "info_agrega_riesgos": "Add risks to visualize charts.",
        "info_agrega_riesgos_matriz": "Add risks to show the accumulated matrix."
    }
}

# Inicializa dataframe en session_state
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

with st.sidebar:
    st.title("Opciones / Options")
    idioma = "es"
    if st.checkbox("English / Inglés", value=False):
        idioma = "en"

if idioma == "es":
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto
    tabla_exposicion_mostrar = factor_exposicion
    tabla_probabilidad_mostrar = factor_probabilidad
    clasificar_criticidad_usar = lambda v: next((clas for inf, sup, clas, _ in criticidad_límites if inf < v <= sup), "NO CLASIFICADO")
    textos_usar = textos["es"]
else:
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto
    tabla_exposicion_mostrar = factor_exposicion
    tabla_probabilidad_mostrar = factor_probabilidad
    clasificar_criticidad_usar = lambda v: next(({
        "ACEPTABLE":"ACCEPTABLE",
        "TOLERABLE":"TOLERABLE",
        "INACEPTABLE":"UNACCEPTABLE",
        "INADMISIBLE":"INTOLERABLE"
    }.get(clas, clas) for inf, sup, clas, _ in criticidad_límites if inf < v <= sup), "NO CLASIFICADO")
    textos_usar = textos["en"]

col_form, col_graf = st.columns([3, 2])

with col_form:
    st.title("Calculadora de Riesgos" if idioma=="es" else "Risk Calculator")
    st.subheader(textos_usar["resultados"])

    nombre_riesgo = st.text_input(textos_usar["nombre_riesgo"])
    descripcion = st.text_area(textos_usar["descripcion_riesgo"])

    opciones_impacto_visibles = tabla_tipo_impacto_mostrar.apply(
        lambda row: f"{row['Código']} - {row['Tipo de Impacto']}", axis=1).tolist()
    seleccion_impacto = st.selectbox(textos_usar["tipo_impacto"], opciones_impacto_visibles)
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    justificacion_impacto = tabla_tipo_impacto_mostrar.loc[tabla_tipo_impacto_mostrar["Código"] == codigo_impacto, "Explicación ASIS"].values[0]
    ponderacion_impacto = tabla_tipo_impacto_mostrar.loc[tabla_tipo_impacto_mostrar["Código"] == codigo_impacto, "Ponderación"].values[0]
    st.markdown(f"**{textos_usar['justificacion']}:** {justificacion_impacto}")

    exposicion = st.selectbox(
        textos_usar["factor_exposicion"],
        options=tabla_exposicion_mostrar["Factor"],
        format_func=lambda x: f"{x:.2f} - {tabla_exposicion_mostrar.loc[tabla_exposicion_mostrar['Factor']==x, 'Nivel'].values[0]}"
    )
    probabilidad = st.selectbox(
        textos_usar["factor_probabilidad"],
        options=tabla_probabilidad_mostrar["Factor"],
        format_func=lambda x: f"{x:.2f} - {tabla_probabilidad_mostrar.loc[tabla_probabilidad_mostrar['Factor']==x, 'Nivel'].values[0]}"
    )
    amenaza_deliberada = st.selectbox(
        textos_usar["amenaza_deliberada"],
        options=[1, 2, 3],
        format_func=lambda x: textos_usar["amenaza_deliberada_opciones"][x],
        index=0
    )
    efectividad = st.slider(textos_usar["efectividad_control"], 0, 100, 50)

    impacto = st.number_input(textos_usar["impacto"], min_value=0, max_value=100, value=30, step=1)

    btn_agregar = st.button(textos_usar["agregar_riesgo"])

# -----------------------------------------
# CÁLCULOS MATEMÁTICOS Y LÓGICOS AL FINAL
# -----------------------------------------

def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto):
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

def clasificar_criticidad(valor):
    for limite_inf, limite_sup, clasif, color in criticidad_límites:
        if limite_inf < valor <= limite_sup:
            return clasif, color
    return "NO CLASIFICADO", "#000000"

if btn_agregar:
    if nombre_riesgo.strip() == "":
        st.error("Debe ingresar un nombre para el riesgo.")
    else:
        efectividad_norm = efectividad / 100
        amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual = calcular_criticidad(
            probabilidad, exposicion, amenaza_deliberada, efectividad_norm, impacto, ponderacion_impacto
        )
        clasificacion, color = clasificar_criticidad(riesgo_residual)

        nuevo = {
            "Nombre Riesgo": nombre_riesgo,
            "Descripción": descripcion,
            "Tipo Impacto": codigo_impacto,
            "Exposición": exposicion,
            "Probabilidad": probabilidad,
            "Amenaza Deliberada": amenaza_deliberada,
            "Efectividad Control (%)": efectividad,
            "Impacto": impacto,
            "Amenaza Inherente": amenaza_inherente,
            "Amenaza Residual": amenaza_residual,
            "Amenaza Residual Ajustada": amenaza_residual_ajustada,
            "Riesgo Residual": riesgo_residual,
            "Clasificación Criticidad": clasificacion,
            "Color Criticidad": color
        }
        st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo])], ignore_index=True)
        st.success(textos_usar["exito_agregar"])

with col_graf:
    st.header(textos_usar["mapa_calor_titulo"])

    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos"])
    else:
        # Mapa de calor: Eje X = Impacto, Eje Y = Riesgo Residual
        df_heatmap = st.session_state.riesgos.copy()

        # Crear bins para Impacto (que es el valor único ingresado en cada riesgo)
        bins_impacto = [0, 20, 40, 60, 80, 100]
        labels_impacto = ["0-20", "21-40", "41-60", "61-80", "81-100"]
        df_heatmap["Impacto Rango"] = pd.cut(df_heatmap["Impacto"].astype(float), bins=bins_impacto, labels=labels_impacto, include_lowest=True)

        # Agregamos riesgo residual promedio por rango impacto para Y, y para X usamos rango impacto categórico
        pivot_heatmap = df_heatmap.groupby("Impacto Rango").agg({
            "Riesgo Residual": "mean"
        }).reindex(labels_impacto).fillna(0)

        # Construir figura Heatmap con riesgo residual vs impacto (rango)
        fig_heatmap = go.Figure(data=go.Bar(
            x=pivot_heatmap.index.astype(str),
            y=pivot_heatmap["Riesgo Residual"],
            marker_color='crimson'
        ))
        fig_heatmap.update_layout(
            title="Riesgo Residual promedio por rango de Impacto",
            xaxis_title="Impacto",
            yaxis_title="Riesgo Residual",
            margin=dict(l=40, r=40, t=40, b=40)
        )

        st.plotly_chart(fig_heatmap, use_container_width=True)

    st.header(textos_usar["pareto_titulo"])
    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos"])
    else:
        df_pareto = st.session_state.riesgos.groupby("Nombre Riesgo").agg({"Riesgo Residual": "sum"}).sort_values(by="Riesgo Residual", ascending=False)
        df_pareto["% Acumulado"] = df_pareto["Riesgo Residual"].cumsum() / df_pareto["Riesgo Residual"].sum() * 100
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(x=df_pareto.index, y=df_pareto["Riesgo Residual"], name="Riesgo Residual"))
        fig_pareto.add_trace(go.Scatter(x=df_pareto.index, y=df_pareto["% Acumulado"], mode="lines+markers", name="% Acumulado", yaxis="y2"))
        fig_pareto.update_layout(
            yaxis=dict(title="Riesgo Residual"),
            yaxis2=dict(title="% Acumulado", overlaying="y", side="right"),
            margin=dict(l=50, r=50, t=50, b=50),
            legend=dict(x=0.8, y=1.1)
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

st.header(textos_usar["matriz_acumulativa_titulo"])

if st.session_state.riesgos.empty:
    st.info(textos_usar["info_agrega_riesgos_matriz"])
else:
    df_matriz = st.session_state.riesgos[[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad"
    ]].copy()

    def estilo_fila_criticidad(row):
        color = st.session_state.riesgos.loc[row.name, "Color Criticidad"]
        return ['background-color: ' + color if col == "Clasificación Criticidad" else '' for col in row.index]

    st.dataframe(df_matriz.style.apply(estilo_fila_criticidad, axis=1), use_container_width=True)

    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Matriz de Riesgos')
        writer.save()
        processed_data = output.getvalue()
        return processed_data

    excel_data = to_excel(df_matriz)

    st.download_button(
        label=textos_usar["descargar_excel"],
        data=excel_data,
        file_name='matriz_de_riesgos.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

