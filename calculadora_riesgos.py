import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap

st.set_page_config(layout="wide")

# Textos traducidos
textos = {
    "es": {
        "factor_exposicion_titulo": "Factor de Exposición",
        "factor_probabilidad_titulo": "Factor de Probabilidad",
        "impacto_severidad_titulo": "Impacto / Severidad",
        "tipo_impacto_titulo": "Tipo de Impacto y Justificación",
        "indice_criticidad_titulo": "Índice de Criticidad",
        "indice_criticidad_descripcion": """
            <ul>
                <li style='color:green;'>Verde: Aceptable (≤ 0.7)</li>
                <li style='color:gold;'>Amarillo: Tolerable (≤ 3)</li>
                <li style='color:orange;'>Naranja: Inaceptable (≤ 7)</li>
                <li style='color:red;'>Rojo: Inadmisible (> 7)</li>
            </ul>
        """,
        "resultados": "Resultados",
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion_riesgo": "Descripción del riesgo",
        "tipo_impacto": "Tipo de Impacto",
        "justificacion": "Justificación",
        "factor_exposicion": "Factor de Exposición",
        "factor_probabilidad": "Factor de Probabilidad",
        "amenaza_deliberada": "Amenaza Deliberada",
        "amenaza_deliberada_opciones": {1: "Baja", 2: "Intermedia", 3: "Alta"},
        "efectividad_control": "Efectividad del control (%)",
        "impacto": "Impacto",
        "amenaza_inherente": "Amenaza Inherente",
        "amenaza_residual": "Amenaza Residual",
        "amenaza_residual_ajustada": "Amenaza Residual Ajustada (x Amenaza Deliberada)",
        "riesgo_residual": "Riesgo Residual",
        "clasificacion": "Clasificación",
        "agregar_riesgo": "Agregar riesgo a la matriz",
        "exito_agregar": "Riesgo agregado a la matriz acumulativa.",
        "mapa_calor_titulo": "Mapa de Calor por Tipo de Impacto y Probabilidad vs Impacto",
        "info_agrega_riesgos": "Agrega riesgos para mostrar el mapa de calor.",
        "matriz_acumulativa_titulo": "Matriz Acumulativa de Riesgos",
        "info_agrega_riesgos_matriz": "Agrega riesgos para mostrar la matriz acumulativa.",
        "descargar_excel": "Descargar matriz de riesgos en Excel"
    },
    "en": {
        "factor_exposicion_titulo": "Exposure Factor",
        "factor_probabilidad_titulo": "Probability Factor",
        "impacto_severidad_titulo": "Impact / Severity",
        "tipo_impacto_titulo": "Impact Type and Justification",
        "indice_criticidad_titulo": "Criticality Index",
        "indice_criticidad_descripcion": """
            <ul>
                <li style='color:green;'>Green: Acceptable (≤ 0.7)</li>
                <li style='color:gold;'>Yellow: Tolerable (≤ 3)</li>
                <li style='color:orange;'>Orange: Unacceptable (≤ 7)</li>
                <li style='color:red;'>Red: Inadmissible (> 7)</li>
            </ul>
        """,
        "resultados": "Results",
        "nombre_riesgo": "Risk Name",
        "descripcion_riesgo": "Risk Description",
        "tipo_impacto": "Impact Type",
        "justificacion": "Justification",
        "factor_exposicion": "Exposure Factor",
        "factor_probabilidad": "Probability Factor",
        "amenaza_deliberada": "Deliberate Threat",
        "amenaza_deliberada_opciones": {1: "Low", 2: "Intermediate", 3: "High"},
        "efectividad_control": "Control Effectiveness (%)",
        "impacto": "Impact",
        "amenaza_inherente": "Inherent Threat",
        "amenaza_residual": "Residual Threat",
        "amenaza_residual_ajustada": "Adjusted Residual Threat (x Deliberate Threat)",
        "riesgo_residual": "Residual Risk",
        "clasificacion": "Classification",
        "agregar_riesgo": "Add risk to matrix",
        "exito_agregar": "Risk added to the cumulative matrix.",
        "mapa_calor_titulo": "Heatmap by Impact Type and Probability vs Impact",
        "info_agrega_riesgos": "Add risks to show the heatmap.",
        "matriz_acumulativa_titulo": "Cumulative Risk Matrix",
        "info_agrega_riesgos_matriz": "Add risks to show the cumulative matrix.",
        "descargar_excel": "Download risk matrix in Excel"
    }
}

# Tablas fijas solo con datos que no se muestran, se usan para cálculos
tabla_tipo_impacto = pd.DataFrame({
    "Código": ["H", "A", "E", "O", "I", "T", "R", "S", "C"],
    "Tipo de Impacto": [
        "Humano", "Ambiental", "Económico", "Operacional",
        "Infraestructura", "Tecnológico", "Reputacional",
        "Social", "Comercial"
    ],
    "Ponderación": [100, 85, 80, 75, 65, 60, 50, 45, 40],
    "Justificación": [
        "Afecta directamente la vida, salud o integridad de las personas. Prioridad máxima según ISO 45001.",
        "Daños ecológicos pueden ser irreversibles y conllevan sanciones graves. ISO 14001.",
        "Pérdidas financieras afectan continuidad y viabilidad del negocio. COSO ERM.",
        "Interrumpe procesos críticos, producción o servicios clave. ISO 22301.",
        "Daño físico a instalaciones o activos afecta operaciones y seguridad.",
        "Fallas de sistemas o ciberataques afectan datos y procesos. ISO 27005.",
        "Afecta imagen pública, confianza y puede derivar en sanciones indirectas. COSO ERM.",
        "Impacta comunidades, condiciones laborales o responsabilidad social. ISO 26000.",
        "Pérdida de clientes, contratos o mercado. Es recuperable pero afecta ingresos."
    ]
})

tabla_exposicion = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
    "Descripcion": [
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

tabla_impacto = pd.DataFrame({
    "Nivel": [1, 2, 3, 4, 5],
    "Valor": [5, 10, 30, 60, 85],
    "Descripcion": [
        "No afecta significativamente",
        "Afectación menor",
        "Afectación parcial y temporal",
        "Afectación significativa",
        "Impacto serio o pérdida total"
    ]
})

# Clasificación ajustada según rango que pediste
def clasificar_criticidad(valor):
    if valor <= 0.7:
        return "ACEPTABLE", "#008000"  # Verde
    elif valor <= 3:
        return "TOLERABLE", "#FFD700"  # Amarillo
    elif valor <= 7:
        return "INACEPTABLE", "#FF8C00"  # Naranja
    else:
        return "INADMISIBLE", "#FF0000"  # Rojo

# Cálculo riesgo
def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto):
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

# Selector idioma en sidebar
with st.sidebar.expander("Language / Idioma", expanded=True):
    idioma = st.selectbox("Selecciona idioma / Select language", options=["es", "en"], index=0)

# Textos idioma actual
t = textos[idioma]

st.title("Calculadora de Riesgos" if idioma == "es" else "Risk Calculator")

# Formulario para ingresar datos del riesgo
nombre_riesgo = st.text_input(t["nombre_riesgo"])
descripcion = st.text_area(t["descripcion_riesgo"])

# Opciones listas desplegables con formato "valor + texto"
opciones_impacto = tabla_tipo_impacto.apply(lambda r: f"{r['Código']} - {r['Tipo de Impacto']}", axis=1).tolist()
seleccion_impacto = st.selectbox(t["tipo_impacto"], opciones_impacto)
codigo_impacto = seleccion_impacto.split(" - ")[0]
justificacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Justificación"].values[0]
ponderacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Ponderación"].values[0]
st.markdown(f"**{t['justificacion']}:** {justificacion_impacto}")

exposicion = st.selectbox(
    t["factor_exposicion"],
    options=tabla_exposicion["Factor"],
    format_func=lambda x: f"{x} {tabla_exposicion.loc[tabla_exposicion['Factor'] == x, 'Nivel'].values[0]}"
)
probabilidad = st.selectbox(
    t["factor_probabilidad"],
    options=tabla_probabilidad["Factor"],
    format_func=lambda x: f"{x} {tabla_probabilidad.loc[tabla_probabilidad['Factor'] == x, 'Nivel'].values[0]}"
)
amenaza_deliberada = st.selectbox(
    t["amenaza_deliberada"],
    options=[1, 2, 3],
    format_func=lambda x: t["amenaza_deliberada_opciones"][x],
    index=0
)
efectividad = st.slider(t["efectividad_control"], 0, 100, 50)
impacto = st.selectbox(
    t["impacto"],
    options=tabla_impacto["Nivel"],
    format_func=lambda x: f"{x} {tabla_impacto.loc[tabla_impacto['Nivel'] == x, 'Descripcion'].values[0]}"
)

efectividad_norm = efectividad / 100
valor_impacto = tabla_impacto.loc[tabla_impacto["Nivel"] == impacto, "Valor"].values[0]

amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual = calcular_criticidad(
    probabilidad, exposicion, amenaza_deliberada, efectividad_norm, valor_impacto, ponderacion_impacto
)

clasificacion, color = clasificar_criticidad(riesgo_residual)

st.markdown(f"### {t['resultados']}:")
st.write(f"- {t['amenaza_inherente']}: {amenaza_inherente:.4f}")
st.write(f"- {t['amenaza_residual']}: {amenaza_residual:.4f}")
st.write(f"- {t['amenaza_residual_ajustada']}: {amenaza_residual_ajustada:.4f}")
st.write(f"- {t['riesgo_residual']}: {riesgo_residual:.4f}")
st.markdown(f"- {t['clasificacion']}: <span style='color:{color};font-weight:bold'>{clasificacion}</span>", unsafe_allow_html=True)

if st.button(t["agregar_riesgo"]) and nombre_riesgo.strip() != "":
    nuevo_riesgo = {
        "Nombre Riesgo": nombre_riesgo.strip(),
        "Descripción": descripcion.strip(),
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
    st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
    st.success(t["exito_agregar"])

# Mostrar matriz acumulativa
st.header(t["matriz_acumulativa_titulo"])

if not st.session_state.riesgos.empty:
    st.dataframe(st.session_state.riesgos.style.applymap(
        lambda c: f"background-color: {c}" if c in ["#008000", "#FFD700", "#FF8C00", "#FF0000"] else ""
        , subset=["Color Criticidad"]))

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.riesgos.to_excel(writer, sheet_name='Matriz de Riesgos', index=False)
    excel_data = output.getvalue()

    st.download_button(
        label=t["descargar_excel"],
        data=excel_data,
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info(t["info_agrega_riesgos_matriz"])

