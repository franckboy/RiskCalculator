```python project="RiskCalculator" file="risk_calculator.py" version=19
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
import random
import time
import threading

# --- Configuración de la página de Streamlit ---
st.set_page_config(layout="wide")

# --- CSS personalizado ---
st.markdown(
    """
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
    @media (max-width: 768px) {
        .dataframe {
            overflow-x: auto;
        }
    }
    .grafico-header {
        font-size: 1.2em !important;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- Tablas base ---
tabla_tipo_impacto = pd.DataFrame(
    {
        "Código": ["H", "O", "E", "I", "T", "R", "A", "C", "S"],
        "Tipo de Impacto": [
            "Humano (H)",
            "Operacional (O)",
            "Económico (E)",
            "Infraestructura (I)",
            "Tecnológico (T)",
            "Reputacional (R)",
            "Ambiental (A)",
            "Comercial (C)",
            "Social (S)",
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
            "Impacto comunitario: Solo crítico en sectores con alta interacción social (ej. minería).",
        ],
    }
)

factor_exposicion = pd.DataFrame(
    {
        "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
        "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
        "Definición": [
            "Exposición extremadamente rara",
            "Exposición ocasional (cada 10 años)",
            "Exposición algunas veces al año",
            "Exposición mensual",
            "Exposición frecuente o semanal",
        ],
    }
)

factor_probabilidad = pd.DataFrame(
    {
        "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
        "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta"],
        "Descripcion": [
            "En condiciones excepcionales",
            "Ha sucedido alguna vez",
            "Podría ocurrir ocasionalmente",
            "Probable en ocasiones",
            "Ocurre con frecuencia / inminente",
        ],
    }
)

# --- Límites de criticidad ---
criticidad_límites = [
    (0, 0.7, "ACEPTABLE", "#008000"),
    (0.7, 3, "TOLERABLE", "#FFD700"),
    (3, 7, "INACEPTABLE", "#FF8C00"),
    (7, float("inf"), "INADMISIBLE", "#FF0000"),
]

# --- Textos para la interfaz ---
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
        "info_agrega_riesgos_matriz": "Agrega riesgos para mostrar la matriz acumulativa.",
        "scatter_titulo": "Gráfico de Dispersión - Probabilidad vs Impacto",
        "stacked_titulo": "Gráfico de Barras Apiladas - Riesgo por Tipo de Impacto",
        "montecarlo_titulo": "Simulación de Monte Carlo",
        "num_iteraciones": "Número de iteraciones",
        "probabilidad_min": "Probabilidad Mínima",
        "probabilidad_max": "Probabilidad Máxima",
        "impacto_min": "Impacto Mínimo",
        "impacto_max": "Impacto Máximo",
        "peso_adicional": "Peso Adicional (%)",
        "error_porcentaje_negativo": "El porcentaje no puede ser negativo.",
        "error_porcentaje_suma": "La suma de los porcentajes debe ser 100%.",
        "validando_porcentajes": "Validando porcentajes...",
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
        "info_agrega_riesgos_matriz": "Add risks to show the accumulated matrix.",
        "scatter_titulo": "Scatter Plot - Probability vs Impact",
        "stacked_titulo": "Stacked Bar Chart - Risk by Impact Type",
        "montecarlo_titulo": "Monte Carlo Simulation",
        "num_iteraciones": "Number of Iterations",
        "probabilidad_min": "Minimum Probability",
        "probabilidad_max": "Maximum Probability",
        "impacto_min": "Minimum Impact",
        "impacto_max": "Maximum Impact",
        "peso_adicional": "Additional Weight (%)",
        "error_porcentaje_negativo": "Percentage cannot be negative.",
        "error_porcentaje_suma": "The sum of the percentages must be 100%.",
        "validando_porcentajes": "Validating percentages...",
    },
}

# --- Inicialización de session_state ---
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(
        columns=[
            "Nombre Riesgo",
            "Descripción",
            "Tipo Impacto",
            "Exposición",
            "Probabilidad",
            "Amenaza Deliberada",
            "Efectividad Control (%)",
            "Impacto",
            "Amenaza Inherente",
            "Amenaza Residual",
            "Amenaza Residual Ajustada",
            "Riesgo Residual",
            "Clasificación Criticidad",
            "Color Criticidad",
        ]
    )

if "total_porcentaje" not in st.session_state:
    st.session_state.total_porcentaje = 0
if "porcentajes_validos" not in st.session_state:
    st.session_state.porcentajes_validos = True
if "validacion_completa" not in st.session_state:
    st.session_state.validacion_completa = False

# --- Funciones de cálculo ---
def calcular_criticidad(
    probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto, peso_adicional
):
    """Calcula la criticidad del riesgo."""
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = (
        amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100) * peso_adicional
    )
    return (
        amenaza_inherente,
        amenaza_residual,
        amenaza_residual_ajustada,
        riesgo_residual,
    )


def clasificar_criticidad(valor):
    """Clasifica la criticidad del riesgo según los límites definidos."""
    for limite_inf, limite_sup, clasif, color in criticidad_límites:
        if limite_inf < valor <= limite_sup:
            return clasif, color
    return "NO CLASIFICADO", "#000000"


# --- Funciones de validación ---
def validar_porcentajes(pesos_adicionales):
    """Valida los porcentajes en un hilo separado."""
    time.sleep(1)  # Simula un tiempo de espera para la validación
    total = sum(pesos_adicionales.values())
    st.session_state.total_porcentaje = total
    st.session_state.porcentajes_validos = abs(total - 100) <= 1e-6
    st.session_state.validacion_completa = True
    st.experimental_rerun()


# --- Funciones de visualización ---
def crear_mapa_calor(df):
    """Crea un mapa de calor para visualizar la distribución de los riesgos."""
    df_heatmap = df.copy()

    bins_impacto = [0, 20, 40, 60, 80, 100]
    labels_impacto = ["0-20", "21-40", "41-60", "61-80", "81-100"]
    df_heatmap["Impacto Rango"] = pd.cut(
        df_heatmap["Impacto"].astype(float),
        bins=bins_impacto,
        labels=labels_impacto,
        include_lowest=True,
    )

    bins_riesgo_residual = [0, 0.7, 3, 7, float("inf")]
    labels_riesgo_residual = ["0-0.7", "0.7-3", "3-7", "7+"]
    df_heatmap["Riesgo Residual Rango"] = pd.cut(
        df_heatmap["Riesgo Residual"].astype(float),
        bins=bins_riesgo_residual,
        labels=labels_riesgo_residual,
        include_lowest=True,
        right=False,
    )

    heatmap_data = (
        df_heatmap.groupby(["Riesgo Residual Rango", "Impacto Rango"])
        .size()
        .unstack(fill_value=0)
    )

    heatmap_data = heatmap_data.reindex(labels_riesgo_residual, axis=0).fillna(0)
    heatmap_data = heatmap_data.reindex(labels_impacto, axis=1).fillna(0)

    colorscale = [
        (0.0, "green"),  # Riesgo bajo
        (0.5, "yellow"),  # Riesgo medio
        (1.0, "red"),  # Riesgo alto
    ]

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns.astype(str),
            y=heatmap_data.index.astype(str),
            colorscale=colorscale,
        )
    )

    fig_heatmap.update_layout(
        title="Mapa de Calor de Riesgos",
        xaxis_title="Rango de Impacto",
        yaxis_title="Rango de Riesgo Residual",
        margin=dict(l=40, r=40, t=40, b=40),
    )

    return fig_heatmap


def crear_diagrama_pareto(df):
    """Crea un diagrama de Pareto para identificar los riesgos más significativos."""
    df_pareto = (
        df.groupby("Nombre Riesgo")
        .agg({"Riesgo Residual": "sum"})
        .sort_values(by="Riesgo Residual", ascending=False)
    )
    df_pareto["% Acumulado"] = (
        df_pareto["Riesgo Residual"].cumsum() / df_pareto["Riesgo Residual"].sum() * 100
    )

    fig_pareto = go.Figure()
    fig_pareto.add_trace(
        go.Bar(x=df_pareto.index, y=df_pareto["Riesgo Residual"], name="Riesgo Residual")
    )
    fig_pareto.add_trace(
        go.Scatter(
            x=df_pareto.index,
            y=df_pareto["% Acumulado"],
            mode="lines+markers",
            name="% Acumulado",
            yaxis="y2",
        )
    )

    fig_pareto.update_layout(
        yaxis=dict(title="Riesgo Residual"),
        yaxis2=dict(title="% Acumulado", overlaying="y", side="right"),
        margin=dict(l=50, r=50, t=50, b=50),
    )

    return fig_pareto


def crear_grafico_barras_apiladas(df):
    """Crea un gráfico de barras apiladas para visualizar el riesgo por tipo de impacto."""
    df_stacked = df.groupby(["Tipo Impacto", "Nombre Riesgo"]).agg(
        {"Riesgo Residual": "sum"}
    ).unstack(fill_value=0)
    df_stacked.columns = df_stacked.columns.get_level_values(1)

    fig_stacked = go.Figure()
    for riesgo in df_stacked.columns:
        fig_stacked.add_trace(
            go.Bar(x=df_stacked.index, y=df_stacked[riesgo], name=riesgo)
        )

    fig_stacked.update_layout(
        xaxis_title="Tipo de Impacto",
        yaxis_title="Riesgo Residual",
        margin=dict(l=40, r=40, t=40, b=40),
        barmode="stack",
    )

    return fig_stacked


# --- Sidebar ---
with st.sidebar:
    st.title("Opciones / Options")
    idioma = "es"
    if st.checkbox("English / Inglés", value=False):
        idioma = "en"

    st.subheader("Pesos Adicionales por Tipo de Impacto")
    pesos_adicionales = {}
    porcentajes_validos = True

    validation_message_container = st.empty()

    for codigo in tabla_tipo_impacto["Código"]:
        if f"peso_adicional_{codigo}" not in st.session_state:
            st.session_state[f"peso_adicional_{codigo}"] = (
                100 / len(tabla_tipo_impacto["Código"])
            )

        peso = st.number_input(
            f"Peso Adicional {codigo} (%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state[f"peso_adicional_{codigo}"],
            step=5.0,
            key=f"slider_{codigo}",
        )

        if peso < 0:
            st.sidebar.error(
                f"{textos[idioma]['error_porcentaje_negativo']} ({codigo})"
            )
            porcentajes_validos = False
        pesos_adicionales[codigo] = peso
        st.session_state[f"peso_adicional_{codigo}"] = peso

    if not st.session_state.validacion_completa:
        with validation_message_container:
            st.info(textos[idioma]["validando_porcentajes"])
        thread = threading.Thread(target=validar_porcentajes, args=(pesos_adicionales,))
        thread.start()
    else:
        validation_message_container.empty()

    if not st.session_state.porcentajes_validos:
        st.sidebar.warning(
            f"La suma de los porcentajes es {st.session_state.total_porcentaje:.2f}%.  Debería ser 100%."
        )

# --- Selección de idioma ---
tabla_tipo_impacto_mostrar = tabla_tipo_impacto
tabla_exposicion_mostrar = factor_exposicion
tabla_probabilidad_mostrar = factor_probabilidad
clasificar_criticidad_usar = lambda v: next(
    (clas for inf, sup, clas, _ in criticidad_límites if inf < v <= sup),
    "NO CLASIFICADO",
)
textos_usar = textos[idioma]

# --- Columnas principales ---
col_form, col_graf = st.columns([3, 2])

# --- Formulario de entrada de datos ---
with col_form:
    st.title("Calculadora de Riesgos" if idioma == "es" else "Risk Calculator")
    st.subheader(textos_usar["resultados"])

    nombre_riesgo = st.text_input(textos_usar["nombre_riesgo"])
    descripcion = st.text_area(textos_usar["descripcion_riesgo"])

    opciones_impacto_visibles = tabla_tipo_impacto_mostrar.apply(
        lambda row: f"{row['Código']} - {row['Tipo de Impacto']}", axis=1
    ).tolist()
    seleccion_impacto = st.selectbox(
        textos_usar["tipo_impacto"], opciones_impacto_visibles
    )
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    justificacion_impacto = tabla_tipo_impacto_mostrar.loc[
        tabla_tipo_impacto_mostrar["Código"] == codigo_impacto, "Explicación ASIS"
    ].values[0]
    ponderacion_impacto = tabla_tipo_impacto_mostrar.loc[
        tabla_tipo_impacto_mostrar["Código"] == codigo_impacto, "Ponderación"
    ].values[0]
    st.markdown(f"**{textos_usar['justificacion']}:** {justificacion_impacto}")

    exposicion = st.selectbox(
        textos_usar["factor_exposicion"],
        options=tabla_exposicion_mostrar["Factor"],
        format_func=lambda x: f"{x:.2f} - {tabla_exposicion_mostrar.loc[tabla_exposicion_mostrar['Factor']==x, 'Nivel'].values[0]}",
    )
    probabilidad = st.selectbox(
        textos_usar["factor_probabilidad"],
        options=tabla_probabilidad_mostrar["Factor"],
        format_func=lambda x: f"{x:.2f} - {tabla_probabilidad_mostrar.loc[tabla_probabilidad_mostrar['Factor']==x, 'Nivel'].values[0]}",
    )
    amenaza_deliberada = st.selectbox(
        textos_usar["amenaza_deliberada"],
        options=[1, 2, 3],
        format_func=lambda x: textos_usar["amenaza_deliberada_opciones"][x],
        index=0,
    )
    efectividad = st.slider(textos_usar["efectividad_control"], 0, 100, 50)

    impacto = st.number_input(
        textos_usar["impacto"], min_value=0, max_value=100, value=30, step=1
    )

    btn_agregar = st.button(textos_usar["agregar_riesgo"])

    if btn_agregar:
        if nombre_riesgo.strip() == "":
            st.error("Debe ingresar un nombre para el riesgo.")
        elif not st.session_state.porcentajes_validos:
            st.error(textos_usar["error_porcentaje_suma"])
        else:
            efectividad_norm = efectividad / 100
            (
                amenaza_inherente,
                amenaza_residual,
                amenaza_residual_ajustada,
                riesgo_residual,
            ) = calcular_criticidad(
                probabilidad,
                exposicion,
                amenaza_deliberada,
                efectividad_norm,
                impacto,
                ponderacion_impacto,
                pesos_adicionales[codigo_impacto] / 100,
            )
            clasificacion, color = clasificar_criticidad(riesgo_residual)

            st.write(f"**Riesgo Residual:** {riesgo_residual:.2f}")
            st.markdown(
                f"**Clasificación:** <span style='color:{color};'>{clasificacion}</span>",
                unsafe_allow_html=True,
            )

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
                "Color Criticidad": color,
            }
            st.session_state.riesgos = pd.concat(
                [st.session_state.riesgos, pd.DataFrame([nuevo])], ignore_index=True
            )
            st.success(textos_usar["exito_agregar"])

    st.subheader(textos_usar["matriz_acumulativa_titulo"])

    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos_matriz"])
    else:
        df_matriz = st.session_state.riesgos[
            [
                "Nombre Riesgo",
                "Descripción",
                "Tipo Impacto",
                "Exposición",
                "Probabilidad",
                "Amenaza Deliberada",
                "Efectividad Control (%)",
                "Impacto",
                "Amenaza Inherente",
                "Amenaza Residual",
                "Amenaza Residual Ajustada",
                "Riesgo Residual",
                "Clasificación Criticidad",
            ]
        ].copy()

        def estilo_fila_criticidad(row):
            color = st.session_state.riesgos.loc[row.name, "Color Criticidad"]
            return [
                "background-color: " + color if col == "Clasificación Criticidad" else ""
                for col in row.index
            ]

        st.dataframe(df_matriz.style.apply(estilo_fila_criticidad, axis=1), use_container_width=True)

        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine="xlsxwriter")
            df.to_excel(writer, index=False, sheet_name="Matriz de Riesgos")
            processed_data = output.getvalue()
            return processed_data

        excel_data = to_excel(df_matriz)

        st.download_button(
            label=textos_usar["descargar_excel"],
            data=excel_data,
            file_name="matriz_de_riesgos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# --- Análisis de Sensibilidad ---
    st.subheader("Análisis de Sensibilidad")
    riesgo_seleccionado = st.selectbox("Seleccione un riesgo para el análisis de sensibilidad", st.session_state.riesgos["Nombre Riesgo"].tolist())

    # Obtener los valores actuales del riesgo seleccionado
    riesgo = st.session_state.riesgos[st.session_state.riesgos["Nombre Riesgo"] == riesgo_seleccionado].iloc[0]

    # Crear sliders para variar los parámetros
    probabilidad_sensibilidad = st.slider("Probabilidad", 0.05, 0.85, float(riesgo["Probabilidad"]), 0.05)
    exposicion_sensibilidad = st.slider("Exposición", 0.05, 0.85, float(riesgo["Exposición"]), 0.05)
    efectividad_sensibilidad = st.slider("Efectividad del Control (%)", 0, 100, int(riesgo["Efectividad Control (%)"]))
    impacto_sensibilidad = st.slider("Impacto", 0, 100, int(riesgo["Impacto"]))

    # Calcular la criticidad con los nuevos valores
    efectividad_norm_sensibilidad = efectividad_sensibilidad / 100
    (
        amenaza_inherente_sensibilidad,
        amenaza_residual_sensibilidad,
        amenaza_residual_ajustada_sensibilidad,
        riesgo_residual_sensibilidad,
    ) = calcular_criticidad(
        probabilidad_sensibilidad,
        exposicion_sensibilidad,
        riesgo["Amenaza Deliberada"],
        efectividad_norm_sensibilidad,
        impacto_sensibilidad,
        ponderacion_impacto,
        pesos_adicionales[riesgo["Tipo Impacto"]] / 100,
    )
    clasificacion_sensibilidad, color_sensibilidad = clasificar_criticidad(riesgo_residual_sensibilidad)

    # Mostrar los resultados del análisis de sensibilidad
    st.write(f"**Riesgo Residual (Sensibilidad):** {riesgo_residual_sensibilidad:.2f}")
    st.markdown(
        f"**Clasificación (Sensibilidad):** <span style='color:{color_sensibilidad};'>{clasificacion_sensibilidad}</span>",
        unsafe_allow_html=True,
    )

# --- Sección de gráficos ---
with col_graf:
    st.markdown("<h2 class='grafico-header'>Mapa de Calor de Riesgos</h2>", unsafe_allow_html=True)
    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos"])
    else:
        fig_heatmap = crear_mapa_calor(st.session_state.riesgos)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("<h2 class='grafico-header'>Pareto - Riesgos Residuales</h2>", unsafe_allow_html=True)
    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos"])
    else:
        fig_pareto = crear_diagrama_pareto(st.session_state.riesgos)
        st.plotly_chart(fig_pareto, use_container_width=True)

    st.markdown("<h2 class='grafico-header'>Gráfico de Barras Apiladas - Riesgo por Tipo de Impacto</h2>", unsafe_allow_html=True)
    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos"])
    else:
        fig_stacked = crear_grafico_barras_apiladas(st.session_state.riesgos)
        st.plotly_chart(fig_stacked, use_container_width=True)
        ```python project="RiskCalculator" file="risk_calculator.py" version=20
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
import random
import time
import threading
import unittest  # Importa el módulo unittest para las pruebas unitarias

# --- Configuración de la página de Streamlit ---
st.set_page_config(layout="wide")

# --- CSS personalizado ---
st.markdown(
    """
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
    @media (max-width: 768px) {
        .dataframe {
            overflow-x: auto;
        }
    }
    .grafico-header {
        font-size: 1.2em !important;
        font-weight: bold;
        margin-bottom: 0.5em;
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- Tablas base ---
tabla_tipo_impacto = pd.DataFrame(
    {
        "Código": ["H", "O", "E", "I", "T", "R", "A", "C", "S"],
        "Tipo de Impacto": [
            "Humano (H)",
            "Operacional (O)",
            "Económico (E)",
            "Infraestructura (I)",
            "Tecnológico (T)",
            "Reputacional (R)",
            "Ambiental (A)",
            "Comercial (C)",
            "Social (S)",
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
            "Impacto comunitario: Solo crítico en sectores con alta interacción social (ej. minería).",
        ],
    }
)

factor_exposicion = pd.DataFrame(
    {
        "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
        "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
        "Definición": [
            "Exposición extremadamente rara",
            "Exposición ocasional (cada 10 años)",
            "Exposición algunas veces al año",
            "Exposición mensual",
            "Exposición frecuente o semanal",
        ],
    }
)

factor_probabilidad = pd.DataFrame(
    {
        "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
        "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta"],
        "Descripcion": [
            "En condiciones excepcionales",
            "Ha sucedido alguna vez",
            "Podría ocurrir ocasionalmente",
            "Probable en ocasiones",
            "Ocurre con frecuencia / inminente",
        ],
    }
)

# --- Límites de criticidad ---
criticidad_límites = [
    (0, 0.7, "ACEPTABLE", "#008000"),
    (0.7, 3, "TOLERABLE", "#FFD700"),
    (3, 7, "INACEPTABLE", "#FF8C00"),
    (7, float("inf"), "INADMISIBLE", "#FF0000"),
]

# --- Textos para la interfaz ---
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
        "info_agrega_riesgos_matriz": "Agrega riesgos para mostrar la matriz acumulativa.",
        "scatter_titulo": "Gráfico de Dispersión - Probabilidad vs Impacto",
        "stacked_titulo": "Gráfico de Barras Apiladas - Riesgo por Tipo de Impacto",
        "montecarlo_titulo": "Simulación de Monte Carlo",
        "num_iteraciones": "Número de iteraciones",
        "probabilidad_min": "Probabilidad Mínima",
        "probabilidad_max": "Probabilidad Máxima",
        "impacto_min": "Impacto Mínimo",
        "impacto_max": "Impacto Máximo",
        "peso_adicional": "Peso Adicional (%)",
        "error_porcentaje_negativo": "El porcentaje no puede ser negativo.",
        "error_porcentaje_suma": "La suma de los porcentajes debe ser 100%.",
        "validando_porcentajes": "Validando porcentajes...",
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
        "info_agrega_riesgos_matriz": "Add risks to show the accumulated matrix.",
        "scatter_titulo": "Scatter Plot - Probability vs Impact",
        "stacked_titulo": "Stacked Bar Chart - Risk by Impact Type",
        "montecarlo_titulo": "Monte Carlo Simulation",
        "num_iteraciones": "Number of Iterations",
        "probabilidad_min": "Minimum Probability",
        "probabilidad_max": "Maximum Probability",
        "impacto_min": "Minimum Impact",
        "impacto_max": "Maximum Impact",
        "peso_adicional": "Additional Weight (%)",
        "error_porcentaje_negativo": "Percentage cannot be negative.",
        "error_porcentaje_suma": "The sum of the percentages must be 100%.",
        "validando_porcentajes": "Validating percentages...",
    },
}

# --- Inicialización de session_state ---
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(
        columns=[
            "Nombre Riesgo",
            "Descripción",
            "Tipo Impacto",
            "Exposición",
            "Probabilidad",
            "Amenaza Deliberada",
            "Efectividad Control (%)",
            "Impacto",
            "Amenaza Inherente",
            "Amenaza Residual",
            "Amenaza Residual Ajustada",
            "Riesgo Residual",
            "Clasificación Criticidad",
            "Color Criticidad",
        ]
    )

if "total_porcentaje" not in st.session_state:
    st.session_state.total_porcentaje = 0
if "porcentajes_validos" not in st.session_state:
    st.session_state.porcentajes_validos = True
if "validacion_completa" not in st.session_state:
    st.session_state.validacion_completa = False

# --- Funciones de cálculo ---
def calcular_criticidad(
    probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto, peso_adicional
):
    """
    Calcula la criticidad del riesgo.

    Args:
        probabilidad (float): Factor de probabilidad del riesgo.
        exposicion (float): Factor de exposición al riesgo.
        amenaza_deliberada (int): Factor que indica si la amenaza es deliberada (1 = No, 2 = Sí baja, 3 = Sí alta).
        efectividad (float): Efectividad de los controles implementados (en porcentaje, por ejemplo, 50% = 0.5).
        valor_impacto (int): Valor numérico que representa el impacto del riesgo.
        ponderacion_impacto (int): Ponderación del tipo de impacto (por ejemplo, Humano = 25, Operacional = 20, etc.).
        peso_adicional (float): Peso adicional configurable por tipo de impacto (en decimal, por ejemplo, 50% = 0.5).

    Returns:
        tuple: Una tupla que contiene la amenaza inherente, la amenaza residual, la amenaza residual ajustada y el riesgo residual.
    """
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = (
        amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100) * peso_adicional
    )
    return (
        amenaza_inherente,
        amenaza_residual,
        amenaza_residual_ajustada,
        riesgo_residual,
    )


def clasificar_criticidad(valor):
    """
    Clasifica la criticidad del riesgo según los límites definidos.

    Args:
        valor (float): El valor del riesgo residual.

    Returns:
        tuple: Una tupla que contiene la clasificación de la criticidad y el color asociado.
    """
    for limite_inf, limite_sup, clasif, color in criticidad_límites:
        if limite_inf < valor <= limite_sup:
            return clasif, color
    return "NO CLASIFICADO", "#000000"


# --- Funciones de validación ---
def validar_porcentajes(pesos_adicionales):
    """
    Valida los porcentajes en un hilo separado.

    Args:
        pesos_adicionales (dict): Un diccionario con los pesos adicionales por tipo de impacto.
    """
    time.sleep(1)  # Simula un tiempo de espera para la validación
    total = sum(pesos_adicionales.values())
    st.session_state.total_porcentaje = total
    st.session_state.porcentajes_validos = abs(total - 100) <= 1e-6
    st.session_state.validacion_completa = True
    st.experimental_rerun()


# --- Funciones de visualización ---
def crear_mapa_calor(df):
    """
    Crea un mapa de calor para visualizar la distribución de los riesgos.

    Args:
        df (pd.DataFrame): El DataFrame con los datos de los riesgos.

    Returns:
        plotly.graph_objects.Figure: La figura del mapa de calor.
    """
    df_heatmap = df.copy()

    bins_impacto = [0, 20, 40, 60, 80, 100]
    labels_impacto = ["0-20", "21-40", "41-60", "61-80", "81-100"]
    df_heatmap["Impacto Rango"] = pd.cut(
        df_heatmap["Impacto"].astype(float),
        bins=bins_impacto,
        labels=labels_impacto,
        include_lowest=True,
    )

    bins_riesgo_residual = [0, 0.7, 3, 7, float("inf")]
    labels_riesgo_residual = ["0-0.7", "0.7-3", "3-7", "7+"]
    df_heatmap["Riesgo Residual Rango"] = pd.cut(
        df_heatmap["Riesgo Residual"].astype(float),
        bins=bins_riesgo_residual,
        labels=labels_riesgo_residual,
        include_lowest=True,
        right=False,
    )

    heatmap_data = (
        df_heatmap.groupby(["Riesgo Residual Rango", "Impacto Rango"])
        .size()
        .unstack(fill_value=0)
    )

    heatmap_data = heatmap_data.reindex(labels_riesgo_residual, axis=0).fillna(0)
    heatmap_data = heatmap_data.reindex(labels_impacto, axis=1).fillna(0)

    colorscale = [
        (0.0, "green"),  # Riesgo bajo
        (0.5, "yellow"),  # Riesgo medio
        (1.0, "red"),  # Riesgo alto
    ]

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns.astype(str),
            y=heatmap_data.index.astype(str),
            colorscale=colorscale,
        )
    )

    fig_heatmap.update_layout(
        title="Mapa de Calor de Riesgos",
        xaxis_title="Rango de Impacto",
        yaxis_title="Rango de Riesgo Residual",
        margin=dict(l=40, r=40, t=40, b=40),
    )

    return fig_heatmap


def crear_diagrama_pareto(df):
    """
    Crea un diagrama de Pareto para identificar los riesgos más significativos.

    Args:
        df (pd.DataFrame): El DataFrame con los datos de los riesgos.

    Returns:
        plotly.graph_objects.Figure: La figura del diagrama de Pareto.
    """
    df_pareto = (
        df.groupby("Nombre Riesgo")
        .agg({"Riesgo Residual": "sum"})
        .sort_values(by="Riesgo Residual", ascending=False)
    )
    df_pareto["% Acumulado"] = (
        df_pareto["Riesgo Residual"].cumsum() / df_pareto["Riesgo Residual"].sum() * 100
    )

    fig_pareto = go.Figure()
    fig_pareto.add_trace(
        go.Bar(x=df_pareto.index, y=df_pareto["Riesgo Residual"], name="Riesgo Residual")
    )
    fig_pareto.add_trace(
        go.Scatter(
            x=df_pareto.index,
            y=df_pareto["% Acumulado"],
            mode="lines+markers",
            name="% Acumulado",
            yaxis="y2",
        )
    )

    fig_pareto.update_layout(
        yaxis=dict(title="Riesgo Residual"),
        yaxis2=dict(title="% Acumulado", overlaying="y", side="right"),
        margin=dict(l=50, r=50, t=50, b=50),
    )

    return fig_pareto


def crear_grafico_barras_apiladas(df):
    """
    Crea un gráfico de barras apiladas para visualizar el riesgo por tipo de impacto.

    Args:
        df (pd.DataFrame): El DataFrame con los datos de los riesgos.

    Returns:
        plotly.graph_objects.Figure: La figura del gráfico de barras apiladas.
    """
    df_stacked = df.groupby(["Tipo Impacto", "Nombre Riesgo"]).agg(
        {"Riesgo Residual": "sum"}
    ).unstack(fill_value=0)
    df_stacked.columns = df_stacked.columns.get_level_values(1)

    fig_stacked = go.Figure()
    for riesgo in df_stacked.columns:
        fig_stacked.add_trace(
            go.Bar(x=df_stacked.index, y=df_stacked[riesgo], name=riesgo)
        )

    fig_stacked.update_layout(
        xaxis_title="Tipo de Impacto",
        yaxis_title="Riesgo Residual",
        margin=dict(l=40, r=40, t=40, b=40),
        barmode="stack",
    )

    return fig_stacked


# --- Pruebas Unitarias ---
class TestCalculoRiesgo(unittest.TestCase):
    """Clase para las pruebas unitarias de las funciones de cálculo de riesgo."""

    def test_calcular_criticidad(self):
        """Prueba la función calcular_criticidad."""
        probabilidad = 0.3
        exposicion = 0.55
        amenaza_deliberada = 2
        efectividad = 0.5
        valor_impacto = 30
        ponderacion_impacto = 25
        peso_adicional = 0.5

        (
            amenaza_inherente,
            amenaza_residual,
            amenaza_residual_ajustada,
            riesgo_residual,
        ) = calcular_criticidad(
            probabilidad,
            exposicion,
            amenaza_deliberada,
            efectividad,
            valor_impacto,
            ponderacion_impacto,
            peso_adicional,
        )

        self.assertAlmostEqual(amenaza_inherente, 0.165)
        self.assertAlmostEqual(amenaza_residual, 0.0825)
        self.assertAlmostEqual(amenaza_residual_ajustada, 0.165)
        self.assertAlmostEqual(riesgo_residual, 0.61875)

    def test_clasificar_criticidad(self):
        """Prueba la función clasificar_criticidad."""
        self.assertEqual(clasificar_criticidad(0.5)[0], "ACEPTABLE")
        self.assertEqual(clasificar_criticidad(2)[0], "TOLERABLE")
        self.assertEqual(clasificar_criticidad(5)[0], "INACEPTABLE")
        self.assertEqual(clasificar_criticidad(8)[0], "INADMISIBLE")


# --- Ejecutar las pruebas unitarias ---
with st.expander("Ejecutar Pruebas Unitarias"):
    if st.button("Ejecutar Pruebas"):
        # Crea un TextTestRunner para mostrar los resultados en Streamlit
        runner = unittest.TextTestRunner(stream=st.text(""), verbosity=2)
        # Crea un TestSuite con las pruebas de la clase TestCalculoRiesgo
        suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculoRiesgo)
        # Ejecuta las pruebas y muestra los resultados
        runner.run(suite)

# --- Sidebar ---
with st.sidebar:
    st.title("Opciones / Options")
    idioma = "es"
    if st.checkbox("English / Inglés", value=False):
        idioma = "en"

    st.subheader("Pesos Adicionales por Tipo de Impacto")
    pesos_adicionales = {}
    porcentajes_validos = True

    validation_message_container = st.empty()

    for codigo in tabla_tipo_impacto["Código"]:
        if f"peso_adicional_{codigo}" not in st.session_state:
            st.session_state[f"peso_adicional_{codigo}"] = (
                100 / len(tabla_tipo_impacto["Código"])
            )

        peso = st.number_input(
            f"Peso Adicional {codigo} (%)",
            min_value=0.0,
            max_value=100.0,
            value=st.session_state[f"peso_adicional_{codigo}"],
            step=5.0,
            key=f"slider_{codigo}",
        )

        if peso < 0:
            st.sidebar.error(
                f"{textos[idioma]['error_porcentaje_negativo']} ({codigo})"
            )
            porcentajes_validos = False
        pesos_adicionales[codigo] = peso
        st.session_state[f"peso_adicional_{codigo}"] = peso

    if not st.session_state.validacion_completa:
        with validation_message_container:
            st.info(textos[idioma]["validando_porcentajes"])
        thread = threading.Thread(target=validar_porcentajes, args=(pesos_adicionales,))
        thread.start()
    else:
        validation_message_container.empty()

    if not st.session_state.porcentajes_validos:
        st.sidebar.warning(
            f"La suma de los porcentajes es {st.session_state.total_porcentaje:.2f}%.  Debería ser 100%."
        )

# --- Selección de idioma ---
tabla_tipo_impacto_mostrar = tabla_tipo_impacto
tabla_exposicion_mostrar = factor_exposicion
tabla_probabilidad_mostrar = factor_probabilidad
clasificar_criticidad_usar = lambda v: next(
    (clas for inf, sup, clas, _ in criticidad_límites if inf < v <= sup),
    "NO CLASIFICADO",
)
textos_usar = textos[idioma]

# --- Columnas principales ---
col_form, col_graf = st.columns([3, 2])

# --- Formulario de entrada de datos ---
with col_form:
    st.title("Calculadora de Riesgos" if idioma == "es" else "Risk Calculator")
    st.subheader(textos_usar["resultados"])

    nombre_riesgo = st.text_input(textos_usar["nombre_riesgo"])
    descripcion = st.text_area(textos_usar["descripcion_riesgo"])

    opciones_impacto_visibles = tabla_tipo_impacto_mostrar.apply(
        lambda row: f"{row['Código']} - {row['Tipo de Impacto']}", axis=1
    ).tolist()
    seleccion_impacto = st.selectbox(
        textos_usar["tipo_impacto"], opciones_impacto_visibles
    )
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    justificacion_impacto = tabla_tipo_impacto_mostrar.loc[
        tabla_tipo_impacto_mostrar["Código"] == codigo_impacto, "Explicación ASIS"
    ].values[0]
    ponderacion_impacto = tabla_tipo_impacto_mostrar.loc[
        tabla_tipo_impacto_mostrar["Código"] == codigo_impacto, "Ponderación"
    ].values[0]
    st.markdown(f"**{textos_usar['justificacion']}:** {justificacion_impacto}")

    exposicion = st.selectbox(
        textos_usar["factor_exposicion"],
        options=tabla_exposicion_mostrar["Factor"],
        format_func=lambda x: f"{x:.2f} - {tabla_exposicion_mostrar.loc[tabla_exposicion_mostrar['Factor']==x, 'Nivel'].values[0]}",
    )
    probabilidad = st.selectbox(
        textos_usar["factor_probabilidad"],
        options=tabla_probabilidad_mostrar["Factor"],
        format_func=lambda x: f"{x:.2f} - {tabla_probabilidad_mostrar.loc[tabla_probabilidad_mostrar['Factor']==x, 'Nivel'].values[0]}",
    )
    amenaza_deliberada = st.selectbox(
        textos_usar["amenaza_deliberada"],
        options=[1, 2, 3],
        format_func=lambda x: textos_usar["amenaza_deliberada_opciones"][x],
        index=0,
    )
    efectividad = st.slider(textos_usar["efectividad_control"], 0, 100, 50)

    impacto = st.number_input(
        textos_usar["impacto"], min_value=0, max_value=100, value=30, step=1
    )

    btn_agregar = st.button(textos_usar["agregar_riesgo"])

    if btn_agregar:
        if nombre_riesgo.strip() == "":
            st.error("Debe ingresar un nombre para el riesgo.")
        elif not st.session_state.porcentajes_validos:
            st.error(textos_usar["error_porcentaje_suma"])
        else:
            efectividad_norm = efectividad / 100
            (
                amenaza_inherente,
                amenaza_residual,
                amenaza_residual_ajustada,
                riesgo_residual,
            ) = calcular_criticidad(
                probabilidad,
                exposicion,
                amenaza_deliberada,
                efectividad_norm,
                impacto,
                ponderacion_impacto,
                pesos_adicionales[codigo_impacto] / 100,
            )
            clasificacion, color = clasificar_criticidad(riesgo_residual)

            st.write(f"**Riesgo Residual:** {riesgo_residual:.2f}")
            st.markdown(
                f"**Clasificación:** <span style='color:{color};'>{clasificacion}</span>",
                unsafe_allow_html=True,
            )

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
                "Color Criticidad": color,
            }
            st.session_state.riesgos = pd.concat(
                [st.session_state.riesgos, pd.DataFrame([nuevo])], ignore_index=True
            )
            st.success(textos_usar["exito_agregar"])

    st.subheader(textos_usar["matriz_acumulativa_titulo"])

    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos_matriz"])
    else:
        df_matriz = st.session_state.riesgos[
            [
                "Nombre Riesgo",
                "Descripción",
                "Tipo Impacto",
                "Exposición",
                "Probabilidad",
                "Amenaza Deliberada",
                "Efectividad Control (%)",
                "Impacto",
                "Amenaza Inherente",
                "Amenaza Residual",
                "Amenaza Residual Ajustada",
                "Riesgo Residual",
                "Clasificación Criticidad",
            ]
        ].copy()

        def estilo_fila_criticidad(row):
            color = st.session_state.riesgos.loc[row.name, "Color Criticidad"]
            return [
                "background-color: " + color if col == "Clasificación Criticidad" else ""
                for col in row.index
            ]

        st.dataframe(df_matriz.style.apply(estilo_fila_criticidad, axis=1), use_container_width=True)

        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine="xlsxwriter")
            df.to_excel(writer, index=False, sheet_name="Matriz de Riesgos")
            processed_data = output.getvalue()
            return processed_data

        excel_data = to_excel(df_matriz)

        st.download_button(
            label=textos_usar["descargar_excel"],
            data=excel_data,
            file_name="matriz_de_riesgos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# --- Análisis de Sensibilidad ---
    st.subheader("Análisis de Sensibilidad")
    riesgo_seleccionado = st.selectbox("Seleccione un riesgo para el análisis de sensibilidad", st.session_state.riesgos["Nombre Riesgo"].tolist())

    # Obtener los valores actuales del riesgo seleccionado
    riesgo = st.session_state.riesgos[st.session_state.riesgos["Nombre Riesgo"] == riesgo_seleccionado].iloc[0]

    # Crear sliders para variar los parámetros
    probabilidad_sensibilidad = st.slider("Probabilidad", 0.05, 0.85, float(riesgo["Probabilidad"]), 0.05)
    exposicion_sensibilidad = st.slider("Exposición", 0.05, 0.85, float(riesgo["Exposición"]), 0.05)
    efectividad_sensibilidad = st.slider("Efectividad del Control (%)", 0, 100, int(riesgo["Efectividad Control (%)"]))
    impacto_sensibilidad = st.slider("Impacto", 0, 100, int(riesgo["Impacto"]))

    # Calcular la criticidad con los nuevos valores
    efectividad_norm_sensibilidad = efectividad_sensibilidad / 100
    (
        amenaza_inherente_sensibilidad,
        amenaza_residual_sensibilidad,
        amenaza_residual_ajustada_sensibilidad,
        riesgo_residual_sensibilidad,
    ) = calcular_criticidad(
        probabilidad_sensibilidad,
        exposicion_sensibilidad,
        riesgo["Amenaza Deliberada"],
        efectividad_norm_sensibilidad,
        impacto_sensibilidad,
        ponderacion_impacto,
        pesos_adicionales[riesgo["Tipo Impacto"]] / 100,
    )
    clasificacion_sensibilidad, color_sensibilidad = clasificar_criticidad(riesgo_residual_sensibilidad)

    # Mostrar los resultados del análisis de sensibilidad
    st.write(f"**Riesgo Residual (Sensibilidad):** {riesgo_residual_sensibilidad:.2f}")
    st.markdown(
        f"**Clasificación (Sensibilidad):** <span style='color:{color_sensibilidad};'>{clasificacion_sensibilidad}</span>",
        unsafe_allow_html=True,
    )

# --- Sección de gráficos ---
with col_graf:
    st.markdown("<h2 class='grafico-header'>Mapa de Calor de Riesgos</h2>", unsafe_allow_html=True)
    if st.session_state.riesgos.
