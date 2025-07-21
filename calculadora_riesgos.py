import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
import random

# Configuración de la página de Streamlit para usar un diseño amplio
st.set_page_config(layout="wide")

# --- CSS personalizado ---
# Se define un estilo CSS personalizado para mejorar la apariencia de los botones y selectores
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

    /* Estilos para la matriz acumulativa en pantallas pequeñas */
    @media (max-width: 768px) {
        .dataframe {
            overflow-x: auto; /* Permite el desplazamiento horizontal */
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

# --- Tablas base ---
# Se definen DataFrames de Pandas que contienen información sobre los tipos de impacto, factores de exposición y factores de probabilidad
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
        "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
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
# Se definen los límites para clasificar la criticidad del riesgo
criticidad_límites = [
    (0, 0.7, "ACEPTABLE", "#008000"),  # Verde
    (0.7, 3, "TOLERABLE", "#FFD700"),  # Amarillo
    (3, 7, "INACEPTABLE", "#FF8C00"),  # Naranja
    (7, float("inf"), "INADMISIBLE", "#FF0000"),  # Rojo
]

# --- Textos para la interfaz ---
# Se definen los textos para la interfaz en español e inglés
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
    },
}

# Inicializa dataframe en session_state
# Se inicializa un DataFrame en el session_state de Streamlit para almacenar los riesgos
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

# --- Sidebar ---
# Se crea una barra lateral para las opciones de configuración
with st.sidebar:
    st.title("Opciones / Options")
    idioma = "es"
    if st.checkbox("English / Inglés", value=False):
        idioma = "en"

# --- Selección de idioma ---
# Se seleccionan los textos y tablas a usar según el idioma seleccionado
if idioma == "es":
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto
    tabla_exposicion_mostrar = factor_exposicion
    tabla_probabilidad_mostrar = factor_probabilidad
    clasificar_criticidad_usar = lambda v: next(
        (clas for inf, sup, clas, _ in criticidad_límites if inf < v <= sup),
        "NO CLASIFICADO",
    )
    textos_usar = textos["es"]
else:
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto
    tabla_exposicion_mostrar = factor_exposicion
    tabla_probabilidad_mostrar = factor_probabilidad
    clasificar_criticidad_usar = lambda v: next(
        (
            {
                "ACEPTABLE": "ACCEPTABLE",
                "TOLERABLE": "TOLERABLE",
                "INACEPTABLE": "UNACCEPTABLE",
                "INADMISIBLE": "INTOLERABLE",
            }.get(clas, clas)
            for inf, sup, clas, _ in criticidad_límites
            if inf < v <= sup
        ),
        "NO CLASIFICADO",
    )
    textos_usar = textos["en"]

# --- Columnas principales ---
# Se divide la interfaz en dos columnas: una para el formulario y otra para los gráficos
col_form, col_graf = st.columns([3, 2])

# --- Formulario de entrada de datos ---
# Se crea el formulario para que el usuario ingrese los datos del riesgo
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


# -----------------------------------------
# CÁLCULOS MATEMÁTICOS Y LÓGICOS AL FINAL
# -----------------------------------------


# --- Función para calcular la criticidad del riesgo ---
# Esta función calcula la amenaza inherente, la amenaza residual, la amenaza residual ajustada y el riesgo residual
def calcular_criticidad(
    probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto
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

    Returns:
        tuple: Una tupla que contiene la amenaza inherente, la amenaza residual, la amenaza residual ajustada y el riesgo residual.
    """
    # Calcula la amenaza inherente multiplicando la probabilidad por la exposición
    amenaza_inherente = probabilidad * exposicion
    # Calcula la amenaza residual aplicando la efectividad de los controles a la amenaza inherente
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    # Calcula la amenaza residual ajustada multiplicando la amenaza residual por el factor de amenaza deliberada
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    # Calcula el riesgo residual multiplicando la amenaza residual ajustada por el valor del impacto y la ponderación del impacto
    riesgo_residual = (
        amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)
    )
    return (
        amenaza_inherente,
        amenaza_residual,
        amenaza_residual_ajustada,
        riesgo_residual,
    )


# --- Función para clasificar la criticidad del riesgo ---
# Esta función clasifica la criticidad del riesgo según los límites definidos en la variable `criticidad_límites`
def clasificar_criticidad(valor):
    """
    Clasifica la criticidad del riesgo según los límites definidos.

    Args:
        valor (float): El valor del riesgo residual.

    Returns:
        tuple: Una tupla que contiene la clasificación de la criticidad y el color asociado.
    """
    # Itera sobre los límites de criticidad y devuelve la clasificación y el color correspondiente
    for limite_inf, limite_sup, clasif, color in criticidad_límites:
        if limite_inf < valor <= limite_sup:
            return clasif, color
    return "NO CLASIFICADO", "#000000"


# --- Proceso al agregar un riesgo ---
# Se ejecuta este código cuando el usuario hace clic en el botón "Agregar riesgo"
if btn_agregar:
    # Valida que se haya ingresado un nombre para el riesgo
    if nombre_riesgo.strip() == "":
        st.error("Debe ingresar un nombre para el riesgo.")
    else:
        # Normaliza la efectividad del control (de porcentaje a decimal)
        efectividad_norm = efectividad / 100
        # Calcula la criticidad del riesgo
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
        )
        # Clasifica la criticidad del riesgo
        clasificacion, color = clasificar_criticidad(riesgo_residual)

        # Crea un diccionario con los datos del nuevo riesgo
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
        # Agrega el nuevo riesgo al DataFrame de riesgos en el session_state
        st.session_state.riesgos = pd.concat(
            [st.session_state.riesgos, pd.DataFrame([nuevo])], ignore_index=True
        )
        # Muestra un mensaje de éxito
        st.success(textos_usar["exito_agregar"])

# --- Sección de gráficos ---
# Se crean los gráficos para visualizar los riesgos
with col_graf:
    # --- Mapa de calor de riesgos ---
    # Se crea un mapa de calor para visualizar la distribución de los riesgos
    st.header(textos_usar["mapa_calor_titulo"])

    # Muestra un mensaje informativo si no hay riesgos agregados
    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos"])
    else:
        # Crea una copia del DataFrame de riesgos
        df_heatmap = st.session_state.riesgos.copy()

        # Define los bins para el impacto y el riesgo residual
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

        # Crea una matriz de conteo de riesgos por rango de impacto y riesgo residual
        heatmap_data = (
            df_heatmap.groupby(["Riesgo Residual Rango", "Impacto Rango"])
            .size()
            .unstack(fill_value=0)
        )

        # Asegura que el índice y las columnas estén en el orden correcto
        heatmap_data = heatmap_data.reindex(labels_riesgo_residual, axis=0).fillna(0)
        heatmap_data = heatmap_data.reindex(labels_impacto, axis=1).fillna(0)

        # Define la escala de colores
        colorscale = [
            (0.0, "green"),  # Riesgo bajo
            (0.5, "yellow"),  # Riesgo medio
            (1.0, "red"),  # Riesgo alto
        ]

        # Construye la figura del mapa de calor
        fig_heatmap = go.Figure(
            data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns.astype(str),
                y=heatmap_data.index.astype(str),
                colorscale=colorscale,
            )
        )

        # Actualiza el diseño del mapa de calor
        fig_heatmap.update_layout(
            title="Mapa de Calor de Riesgos",
            xaxis_title="Rango de Impacto",
            yaxis_title="Rango de Riesgo Residual",
            margin=dict(l=40, r=40, t=40, b=40),
        )

        # Muestra el mapa de calor en Streamlit
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # --- Diagrama de Pareto de riesgos residuales ---
    # Se crea un diagrama de Pareto para identificar los riesgos más significativos
    st.header(textos_usar["pareto_titulo"])
    # Muestra un mensaje informativo si no hay riesgos agregados
    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos"])
    else:
        # Agrupa los riesgos por nombre y calcula la suma del riesgo residual
        df_pareto = (
            st.session_state.riesgos.groupby("Nombre Riesgo")
            .agg({"Riesgo Residual": "sum"})
            .sort_values(by="Riesgo Residual", ascending=False)
        )
        # Calcula el porcentaje acumulado del riesgo residual
        df_pareto["% Acumulado"] = (
            df_pareto["Riesgo Residual"].cumsum()
            / df_pareto["Riesgo Residual"].sum()
            * 100
        )
        # Crea la figura del diagrama de Pareto
        fig_pareto = go.Figure()
        # Agrega las barras del riesgo residual
        fig_pareto.add_trace(
            go.Bar(x=df_pareto.index, y=df_pareto["Riesgo Residual"], name="Riesgo Residual")
        )
        # Agrega la línea del porcentaje acumulado
        fig_pareto.add_trace(
            go.Scatter(
                x=df_pareto.index,
                y=df_pareto["% Acumulado"],
                mode="lines+markers",
                name="% Acumulado",
                yaxis="y2",
            )
        )
        # Actualiza el diseño del diagrama de Pareto
        fig_pareto.update_layout(
            yaxis=dict(title="Riesgo Residual"),
            yaxis2=dict(title="% Acumulado", overlaying="y", side="right"),
            margin=dict(l=50, r=50, t=50, b=50),
            legend=dict(x=0.8, y=1.1),
        )
        # Muestra el diagrama de Pareto en Streamlit
        st.plotly_chart(fig_pareto, use_container_width=True)

    # --- Gráfico de Barras Apiladas ---
    # Se crea un gráfico de barras apiladas para visualizar el riesgo por tipo de impacto
    st.header(textos_usar["stacked_titulo"])
    # Muestra un mensaje informativo si no hay riesgos agregados
    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos"])
    else:
        # Agrupa los riesgos por tipo de impacto y nombre del riesgo, y calcula la suma del riesgo residual
        df_stacked = st.session_state.riesgos.groupby(["Tipo Impacto", "Nombre Riesgo"]).agg(
            {"Riesgo Residual": "sum"}
        ).unstack(fill_value=0)
        # Obtiene los nombres de los riesgos como columnas
        df_stacked.columns = df_stacked.columns.get_level_values(1)

        # Crea la figura del gráfico de barras apiladas
        fig_stacked = go.Figure()
        # Agrega las barras para cada riesgo
        for riesgo in df_stacked.columns:
            fig_stacked.add_trace(
                go.Bar(x=df_stacked.index, y=df_stacked[riesgo], name=riesgo)
            )

        # Actualiza el diseño del gráfico de barras apiladas
        fig_stacked.update_layout(
            xaxis_title="Tipo de Impacto",
            yaxis_title="Riesgo Residual",
            margin=dict(l=40, r=40, t=40, b=40),
            barmode="stack",  # Apilar las barras
        )

        # Muestra el gráfico de barras apiladas en Streamlit
        st.plotly_chart(fig_stacked, use_container_width=True)

    # --- Matriz acumulativa de riesgos ---
    # Se crea una matriz acumulativa para mostrar los datos de los riesgos en formato de tabla
    st.header(textos_usar["matriz_acumulativa_titulo"])

    # Muestra un mensaje informativo si no hay riesgos agregados
    if st.session_state.riesgos.empty:
        st.info(textos_usar["info_agrega_riesgos_matriz"])
    else:
        # Selecciona las columnas a mostrar en la matriz
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

        # Define una función para aplicar estilo a las filas según la criticidad del riesgo
        def estilo_fila_criticidad(row):
            color = st.session_state.riesgos.loc[row.name, "Color Criticidad"]
            return [
                "background-color: " + color if col == "Clasificación Criticidad" else ""
                for col in row.index
            ]

        # Muestra la matriz en Streamlit con estilo aplicado
        st.dataframe(df_matriz.style.apply(estilo_fila_criticidad, axis=1), use_container_width=True)

        # --- Descarga de la matriz en Excel ---
        # Se crea una función para convertir el DataFrame a un archivo Excel
        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine="xlsxwriter")
            df.to_excel(writer, index=False, sheet_name="Matriz de Riesgos")
            processed_data = output.getvalue()
            return processed_data

        # Convierte el DataFrame a un archivo Excel
        excel_data = to_excel(df_matriz)

        # Agrega un botón de descarga para descargar la matriz en Excel
        st.download_button(
            label=textos_usar["descargar_excel"],
            data=excel_data,
            file_name="matriz_de_riesgos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # --- Simulación de Monte Carlo ---
    # Se crea una sección para la simulación de Monte Carlo
    st.header(textos_usar["montecarlo_titulo"])

    # Define los parámetros de la simulación
    num_iteraciones = st.number_input(textos_usar["num_iteraciones"], min_value=100, max_value=10000, value=1000, step=100)
    probabilidad_min = st.number_input(textos_usar["probabilidad_min"], min_value=0.0, max_value=1.0, value=0.1, step=0.01)
    probabilidad_max = st.number_input(textos_usar["probabilidad_max"], min_value=0.0, max_value=1.0, value=0.3, step=0.01)
    impacto_min = st.number_input(textos_usar["impacto_min"], min_value=0, max_value=10000, value=1000, step=100)
    impacto_max = st.number_input(textos_usar["impacto_max"], min_value=0, max_value=10000, value=5000, step=100)

    # Define la función para ejecutar la simulación de Monte Carlo
    def calcular_riesgo_montecarlo(probabilidad_min, probabilidad_max, impacto_min, impacto_max, num_iteraciones):
        resultados = []
        for _ in range(num_iteraciones):
            # Simular la probabilidad (distribución uniforme)
            probabilidad = random.uniform(probabilidad_min, probabilidad_max)
            # Simular el impacto (distribución uniforme)
            impacto = random.uniform(impacto_min, impacto_max)
            # Calcular el riesgo
            riesgo = probabilidad * impacto
            resultados.append(riesgo)
        return resultados

    # Ejecuta la simulación de Monte Carlo
    resultados = calcular_riesgo_montecarlo(probabilidad_min, probabilidad_max, impacto_min, impacto_max, num_iteraciones)

    # Analiza los resultados
    riesgo_promedio = np.mean(resultados)
    riesgo_maximo = np.max(resultados)
    riesgo_minimo = np.min(resultados)
    percentil_95 = np.percentile(resultados, 95)

    # Muestra los resultados
    st.write(f"Riesgo promedio: {riesgo_promedio:.2f}")
    st.write(f"Riesgo máximo: {riesgo_maximo:.2f}")
    st.write(f"Riesgo mínimo: {riesgo_minimo:.2f}")
    st.write(f"Percentil 95: {percentil_95:.2f}")

    # Crea un histograma de los resultados
    fig_histograma = go.Figure(data=[go.Histogram(x=resultados)])
    fig_histograma.update_layout(
        title="Distribución de Resultados de la Simulación de Monte Carlo",
        xaxis_title="Riesgo",
        yaxis_title="Frecuencia",
    )
    st.plotly_chart(fig_histograma, use_container_width=True)
