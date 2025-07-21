import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import base64
import io

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

matriz_probabilidad = pd.DataFrame({
    "Nivel": [1, 2, 3, 4, 5],
    "Clasificacion": ["Rara", "Poco Probable", "Posible", "Probable", "Casi seguro"],
    "Rango": ["≤ 0.05", "0.06 – 0.15", "0.16 – 0.40", "0.41 – 0.70", "> 0.70"],
    "Factor": [0.04, 0.10, 0.25, 0.55, 0.85],
    "Definición": [
        "Evento muy poco probable",
        "Posible en circunstancias poco comunes",
        "Puede ocurrir ocasionalmente",
        "Ocurre con frecuencia",
        "Ocurre casi siempre o siempre"
    ]
})

matriz_impacto = pd.DataFrame({
    "Nivel": [1, 2, 3, 4, 5],
    "Valor": [5, 10, 30, 60, 85],
    "Clasificacion": ["Insignificante", "Leve", "Moderado", "Grave", "Crítico"],
    "Definición": [
        "No afecta significativamente",
        "Afectación menor",
        "Afectación parcial y temporal",
        "Afectación significativa",
        "Impacto serio o pérdida total"
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

efectividad_controles = pd.DataFrame({
    "Rango": ["0%", "1 - 20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
    "Factor": [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0],
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

# Clasificación criticidad y color
def clasificar_criticidad(valor, idioma="es"):
    for limite_inf, limite_sup, clasif, color in criticidad_límites:
        if limite_inf < valor <= limite_sup:
            if idioma == "es":
                return clasif, color
            else:
                traduccion = {
                    "ACEPTABLE": "ACCEPTABLE",
                    "TOLERABLE": "TOLERABLE",
                    "INACEPTABLE": "UNACCEPTABLE",
                    "INADMISIBLE": "INTOLERABLE"
                }
                return traduccion.get(clasif, clasif), color
    return "NO CLASIFICADO", "#000000"

# Cálculo riesgo residual individual (para cada tipo impacto)
def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto):
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

# Estado para riesgos
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

# Selección idioma sidebar
with st.sidebar:
    st.title("Opciones / Options")
    idioma = "es"
    if st.checkbox("English / Inglés", value=False):
        idioma = "en"

if idioma == "es":
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto
    tabla_exposicion_mostrar = factor_exposicion
    tabla_probabilidad_mostrar = factor_probabilidad
    tabla_impacto_mostrar = matriz_impacto
    clasificar_criticidad_usar = lambda v: clasificar_criticidad(v, "es")
    textos_usar = textos["es"]
else:
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto
    tabla_exposicion_mostrar = factor_exposicion
    tabla_probabilidad_mostrar = factor_probabilidad
    tabla_impacto_mostrar = matriz_impacto
    clasificar_criticidad_usar = lambda v: clasificar_criticidad(v, "en")
    textos_usar = textos["en"]

# Layout principal
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
        format_func=lambda x: f"{x:.2f} - {tabla_exposicion_mostrar.loc[tabla_exposicion_mostrar['Factor']==x, 'Nivel'].values[0]} - {tabla_exposicion_mostrar.loc[tabla_exposicion_mostrar['Factor']==x, 'Definición'].values[0]}"
    )

    probabilidad = st.selectbox(
        textos_usar["factor_probabilidad"],
        options=tabla_probabilidad_mostrar["Factor"],
        format_func=lambda x: f"{x:.2f} - {tabla_probabilidad_mostrar.loc[tabla_probabilidad_mostrar['Factor']==x, 'Nivel'].values[0]} - {tabla_probabilidad_mostrar.loc[tabla_probabilidad_mostrar['Factor']==x, 'Descripcion'].values[0]}"
    )

    amenaza_deliberada = st.selectbox(
        textos_usar["amenaza_deliberada"],
        options=list(textos_usar["amenaza_deliberada_opciones"].keys()),
        format_func=lambda x: textos_usar["amenaza_deliberada_opciones"][x]
    )

    efectividad = st.slider(
        textos_usar["efectividad_control"],
        min_value=0,
        max_value=100,
        step=5,
        value=50
    ) / 100

    impacto = st.select_slider(
        textos_usar["impacto"],
        options=tabla_impacto_mostrar["Valor"].tolist(),
        format_func=lambda x: f"{x} - {tabla_impacto_mostrar.loc[tabla_impacto_mostrar['Valor'] == x, 'Clasificacion'].values[0]}"
    )

    if st.button(textos_usar["agregar_riesgo"]):
        if nombre_riesgo.strip() == "":
            st.error("El nombre del riesgo no puede estar vacío.")
        else:
            a_inh, a_res, a_res_adj, r_res = calcular_criticidad(probabilidad, exposicion, amenaza_deliberada, efectividad, impacto, ponderacion_impacto)
            clasif, color = clasificar_criticidad_usar(r_res)

            nuevo = {
                "Nombre Riesgo": nombre_riesgo,
                "Descripción": descripcion,
                "Tipo Impacto": codigo_impacto,
                "Exposición": exposicion,
                "Probabilidad": probabilidad,
                "Amenaza Deliberada": amenaza_deliberada,
                "Efectividad Control (%)": efectividad,
                "Impacto": impacto,
                "Amenaza Inherente": a_inh,
                "Amenaza Residual": a_res,
                "Amenaza Residual Ajustada": a_res_adj,
                "Riesgo Residual": r_res,
                "Clasificación Criticidad": clasif,
                "Color Criticidad": color
            }
            st.session_state.riesgos = st.session_state.riesgos.append(nuevo, ignore_index=True)
            st.success(textos_usar["exito_agregar"])

with col_graf:
    st.subheader(textos_usar["pareto_titulo"])

    if not st.session_state.riesgos.empty:
        df = st.session_state.riesgos.copy()
        df = df.sort_values(by="Riesgo Residual", ascending=False)

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df["Nombre Riesgo"],
            y=df["Riesgo Residual"],
            marker_color=df["Color Criticidad"],
            name="Riesgo Residual"
        ))

        fig.add_trace(go.Scatter(
            x=df["Nombre Riesgo"],
            y=df["Riesgo Residual"].cumsum(),
            mode="lines+markers",
            name="Acumulado"
        ))

        fig.update_layout(
            yaxis_title="Riesgo Residual",
            xaxis_title="Riesgo",
            title=textos_usar["pareto_titulo"],
            height=450,
            margin=dict(l=40, r=20, t=50, b=150),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(textos_usar["info_agrega_riesgos"])

# Matriz Acumulativa y descarga
st.markdown(f"## {textos_usar['matriz_acumulativa_titulo']}")
if not st.session_state.riesgos.empty:
    df = st.session_state.riesgos.copy()
    df_matriz = df.pivot_table(
        index="Probabilidad",
        columns="Impacto",
        values="Riesgo Residual",
        aggfunc="sum"
    ).fillna(0).round(4)

    st.dataframe(df_matriz)

    towrite = BytesIO()
    df_matriz.to_excel(towrite, engine='xlsxwriter')
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="matriz_acumulativa.xlsx">📥 {textos_usar["descargar_excel"]}</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    st.info(textos_usar["info_agrega_riesgos_matriz"])

# Mapa de calor (Probabilidad x Impacto)
def crear_mapa_calor_probabilidad_vs_impacto(df):
    st.markdown(f"## {textos_usar['mapa_calor_titulo']}")

    if df.empty:
        st.warning("No hay datos para mostrar.")
        return

    df["MapaCalor"] = df["Probabilidad"] * df["Impacto"]

    all_prob = sorted(df["Probabilidad"].unique())
    all_impact = sorted(df["Impacto"].unique())

    mapa = df.pivot_table(index="Probabilidad", columns="Impacto", values="MapaCalor", aggfunc="mean")
    mapa = mapa.reindex(index=all_prob, columns=all_impact)

    def clasificar_emoji(valor):
        if pd.isna(valor):
            return ""
        elif valor >= 0.75:
            return "🔴"
        elif valor >= 0.5:
            return "🟠"
        elif valor >= 0.25:
            return "🟡"
        else:
            return "🟢"

    emoji_matrix = mapa.applymap(clasificar_emoji)

    fig, ax = plt.subplots(figsize=(8, 6))
    cmap = LinearSegmentedColormap.from_list("semaforo", ["#00cc44", "#ffff00", "#ff9900", "#cc0000"])
    sns.heatmap(
        mapa, annot=emoji_matrix, fmt="", cmap=cmap, linewidths=1, linecolor='white',
        square=True, mask=mapa.isnull(), vmin=0, vmax=1, cbar=False, ax=ax
    )

    ax.set_title(f"Mapa de Calor - Probabilidad vs Impacto", fontsize=14)
    ax.set_xlabel("Impacto")
    ax.set_ylabel("Probabilidad")

    st.pyplot(fig)

    st.markdown("""
    <div style='text-align:center; margin-top:15px; font-size:16px'>
        <b>Leyenda:</b><br>
        🔴 Inadmisible &nbsp;&nbsp;&nbsp; 🟠 No aceptable &nbsp;&nbsp;&nbsp; 🟡 Aceptable con controles &nbsp;&nbsp;&nbsp; 🟢 Aceptable
    </div>
    """, unsafe_allow_html=True)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="mapa_calor.png">📥 Descargar PNG</a>'
    st.markdown(href, unsafe_allow_html=True)

if not st.session_state.riesgos.empty:
    crear_mapa_calor_probabilidad_vs_impacto(st.session_state.riesgos)
else:
    st.info(textos_usar["info_agrega_riesgos_matriz"])

