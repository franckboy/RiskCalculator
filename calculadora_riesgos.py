import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder

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
                <li style='color:green;'>Verde: Aceptable (≤ 2)</li>
                <li style='color:gold;'>Amarillo: Tolerable (≤ 4)</li>
                <li style='color:orange;'>Naranja: Inaceptable (≤ 15)</li>
                <li style='color:red;'>Rojo: Inadmisible (> 15)</li>
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
                <li style='color:green;'>Green: Acceptable (≤ 2)</li>
                <li style='color:gold;'>Yellow: Tolerable (≤ 4)</li>
                <li style='color:orange;'>Orange: Unacceptable (≤ 15)</li>
                <li style='color:red;'>Red: Inadmissible (> 15)</li>
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

# Tablas fijas traducidas (en español e inglés)
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

tabla_tipo_impacto_en = pd.DataFrame({
    "Code": ["H", "A", "E", "O", "I", "T", "R", "S", "C"],
    "Impact Type": [
        "Human", "Environmental", "Economic", "Operational",
        "Infrastructure", "Technological", "Reputational",
        "Social", "Commercial"
    ],
    "Weighting": [100, 85, 80, 75, 65, 60, 50, 45, 40],
    "Justification": [
        "Directly affects life, health, or integrity of people. Maximum priority per ISO 45001.",
        "Ecological damage may be irreversible with severe sanctions. ISO 14001.",
        "Financial losses affect business continuity and viability. COSO ERM.",
        "Interrupts critical processes, production or key services. ISO 22301.",
        "Physical damage to facilities or assets affects operations and safety.",
        "System failures or cyberattacks affect data and processes. ISO 27005.",
        "Affects public image, trust, may lead to indirect sanctions. COSO ERM.",
        "Impacts communities, labor conditions, or social responsibility. ISO 26000.",
        "Loss of customers, contracts or market. Recoverable but impacts income."
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

tabla_efectividad_en = pd.DataFrame({
    "Range": ["0%", "1 - 20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
    "Factor": [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.1],
    "Mitigation": ["Ineffective", "Limited", "Low", "Intermediate", "High", "Very High", "Total"],
    "Description": [
        "Does not reduce risk",
        "Reduces only under ideal conditions",
        "Mitigates minor risks.",
        "Standard control with limitations.",
        "Significantly reduces risk",
        "Robust and well implemented control.",
        "Eliminates almost all risk"
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

tabla_exposicion_en = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Level": ["Very Low", "Low", "Moderate", "High", "Very High"],
    "Description": [
        "Extremely rare exposure",
        "Occasional exposure (every 10 years)",
        "Exposure a few times a year",
        "Monthly exposure",
        "Frequent or weekly exposure"
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

tabla_probabilidad_en = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Level": ["Very Low", "Low", "Moderate", "High", "Very High"],
    "Description": [
        "Under exceptional conditions",
        "Has happened once",
        "Could occur occasionally",
        "Likely sometimes",
        "Occurs frequently / imminent"
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

tabla_impacto_en = pd.DataFrame({
    "Level": [1, 2, 3, 4, 5],
    "Value": [5, 10, 30, 60, 85],
    "Description": [
        "Does not significantly affect",
        "Minor impact",
        "Partial and temporary impact",
        "Significant impact",
        "Serious impact or total loss"
    ]
})

tabla_criticidad = pd.DataFrame({
    "Límite Superior": [2, 4, 15, float('inf')],
    "Clasificación": ["ACEPTABLE", "TOLERABLE", "INACEPTABLE", "INADMISIBLE"],
    "Color": ["Verde", "Amarillo", "Naranja", "Rojo"]
})

tabla_criticidad_en = pd.DataFrame({
    "Upper Limit": [2, 4, 15, float('inf')],
    "Classification": ["ACCEPTABLE", "TOLERABLE", "UNACCEPTABLE", "INADMISSIBLE"],
    "Color": ["Green", "Yellow", "Orange", "Red"]
})

colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]
cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

def clasificar_criticidad(valor):
    if valor <= 2:
        return "ACEPTABLE", "Verde"
    elif valor <= 4:
        return "TOLERABLE", "Amarillo"
    elif valor <= 15:
        return "INACEPTABLE", "Naranja"
    else:
        return "INADMISIBLE", "Rojo"

def clasificar_criticidad_en(valor):
    if valor <= 2:
        return "ACCEPTABLE", "Green"
    elif valor <= 4:
        return "TOLERABLE", "Yellow"
    elif valor <= 15:
        return "UNACCEPTABLE", "Orange"
    else:
        return "INADMISSIBLE", "Red"

def mostrar_tabla_fija(df, titulo):
    st.markdown(f"### {titulo}")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True, filter=False, sortable=False)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, height=min(200, 35*len(df)), fit_columns_on_grid_load=True, enable_enterprise_modules=False, update_mode='NO_UPDATE')
# Selección de idioma
idioma = st.sidebar.selectbox("Idioma / Language", ["Español", "English"])
lang = "es" if idioma == "Español" else "en"
txt = textos[lang]

st.title(txt["indice_criticidad_titulo"])

# Mostrar tablas fijas según idioma
if lang == "es":
    mostrar_tabla_fija(tabla_tipo_impacto, "Tipos de Impacto y Ponderaciones")
    mostrar_tabla_fija(tabla_efectividad, "Efectividad del Control (%)")
    mostrar_tabla_fija(tabla_exposicion, "Factor de Exposición")
    mostrar_tabla_fija(tabla_probabilidad, "Factor de Probabilidad")
    mostrar_tabla_fija(tabla_impacto, "Impacto")
    mostrar_tabla_fija(tabla_criticidad, "Clasificación de Criticidad")
else:
    mostrar_tabla_fija(tabla_tipo_impacto_en, "Impact Types and Weightings")
    mostrar_tabla_fija(tabla_efectividad_en, "Control Effectiveness (%)")
    mostrar_tabla_fija(tabla_exposicion_en, "Exposure Factor")
    mostrar_tabla_fija(tabla_probabilidad_en, "Probability Factor")
    mostrar_tabla_fija(tabla_impacto_en, "Impact")
    mostrar_tabla_fija(tabla_criticidad_en, "Criticality Classification")

st.markdown("---")

# Contenedor para inputs de riesgo
with st.form(key="form_riesgo"):
    col1, col2 = st.columns(2)

    with col1:
        nombre_riesgo = st.text_input(txt["nombre_riesgo"])
        descripcion_riesgo = st.text_area(txt["descripcion_riesgo"], height=70)
        tipo_impacto = st.selectbox(txt["tipo_impacto"], options=tabla_tipo_impacto["Código"].tolist() if lang == "es" else tabla_tipo_impacto_en["Code"].tolist())
        justificacion = st.text_area(txt["justificacion"], height=50)

    with col2:
        factor_exposicion = st.select_slider(txt["factor_exposicion"], options=tabla_exposicion["Nivel"].tolist() if lang == "es" else tabla_exposicion_en["Level"].tolist())
        factor_probabilidad = st.select_slider(txt["factor_probabilidad"], options=tabla_probabilidad["Nivel"].tolist() if lang == "es" else tabla_probabilidad_en["Level"].tolist())
        amenaza_deliberada = st.select_slider(txt["amenaza_deliberada"], options=list(txt["amenaza_deliberada_opciones"].values()))
        efectividad_control = st.slider(txt["efectividad_control"], min_value=0, max_value=100, value=50)

    enviar = st.form_submit_button(txt["agregar_riesgo"])

# Conversión de selección a valores numéricos
def obtener_factor_desde_nivel(nivel, tabla, lang):
    if lang == "es":
        return tabla.loc[tabla["Nivel"] == nivel, "Factor"].values[0]
    else:
        return tabla.loc[tabla["Level"] == nivel, "Factor"].values[0]

factor_exposicion_val = obtener_factor_desde_nivel(factor_exposicion, tabla_exposicion if lang == "es" else tabla_exposicion_en, lang)
factor_probabilidad_val = obtener_factor_desde_nivel(factor_probabilidad, tabla_probabilidad if lang == "es" else tabla_probabilidad_en, lang)

# Amenaza deliberada numérica
amenaza_deliberada_dict = {v: k for k, v in txt["amenaza_deliberada_opciones"].items()}
amenaza_deliberada_val = amenaza_deliberada_dict.get(amenaza_deliberada, 1)

if enviar:
    st.success(txt["exito_agregar"])
    # Aquí continuarás con el cálculo y la matriz acumulativa
# Obtener valor impacto y ponderación según tipo de impacto seleccionado
if lang == "es":
    fila_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == tipo_impacto].iloc[0]
else:
    fila_impacto = tabla_tipo_impacto_en.loc[tabla_tipo_impacto_en["Code"] == tipo_impacto].iloc[0]

ponderacion_impacto = fila_impacto["Ponderación"]
justificacion_impacto = fila_impacto["Justificación"] if lang == "es" else fila_impacto["Justification"]

valor_impacto = tabla_impacto.loc[tabla_impacto["Nivel"] == 5, "Valor"].values[0]  # Puedes ajustar el impacto si quieres

# Calcular amenaza inherente, residual, ajustada y riesgo residual
amenaza_inherente = factor_probabilidad_val * factor_exposicion_val
efectividad_norm = efectividad_control / 100
amenaza_residual = amenaza_inherente * (1 - efectividad_norm)
amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada_val
riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)

# Función para clasificar riesgo según nuevo criterio
def clasificar_riesgo(valor):
    if valor <= 0.7:
        return ("ACEPTABLE" if lang=="es" else "ACCEPTABLE", "green")
    elif valor <= 3:
        return ("TOLERABLE" if lang=="es" else "TOLERABLE", "yellow")
    elif valor <= 7:
        return ("INACEPTABLE" if lang=="es" else "UNACCEPTABLE", "orange")
    else:
        return ("INADMISIBLE" if lang=="es" else "INADMISSIBLE", "red")

clasificacion, color = clasificar_riesgo(riesgo_residual)

# Mostrar resultados en la app
st.markdown(f"### {txt['resultados']}")
st.write(f"- Amenaza Inherente: {amenaza_inherente:.4f}")
st.write(f"- Amenaza Residual: {amenaza_residual:.4f}")
st.write(f"- Amenaza Residual Ajustada: {amenaza_residual_ajustada:.4f}")
st.write(f"- Riesgo Residual: {riesgo_residual:.4f}")
st.markdown(f"**Clasificación:** <span style='color:{color}'>{clasificacion}</span>", unsafe_allow_html=True)

# Agregar riesgo a la matriz acumulativa
if enviar:
    nuevo_riesgo = {
        "Nombre Riesgo": nombre_riesgo,
        "Descripción": descripcion_riesgo,
        "Tipo Impacto": tipo_impacto,
        "Justificación Impacto": justificacion_impacto,
        "Factor Exposición": factor_exposicion_val,
        "Nivel Exposición": factor_exposicion,
        "Factor Probabilidad": factor_probabilidad_val,
        "Nivel Probabilidad": factor_probabilidad,
        "Amenaza Deliberada": amenaza_deliberada_val,
        "Efectividad Control (%)": efectividad_control,
        "Impacto": valor_impacto,
        "Ponderación Impacto": ponderacion_impacto,
        "Amenaza Inherente": amenaza_inherente,
        "Amenaza Residual": amenaza_residual,
        "Amenaza Residual Ajustada": amenaza_residual_ajustada,
        "Riesgo Residual": riesgo_residual,
        "Clasificación": clasificacion,
        "Color Clasificación": color
    }
    if "matriz_riesgos" not in st.session_state:
        st.session_state.matriz_riesgos = pd.DataFrame()
    st.session_state.matriz_riesgos = pd.concat([st.session_state.matriz_riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)

# Mostrar matriz acumulativa si existe
if "matriz_riesgos" in st.session_state and not st.session_state.matriz_riesgos.empty:
    st.markdown(f"## {txt['matriz_acumulativa_titulo']}")
    def color_fila(row):
        return [f'background-color: {row["Color Clasificación"]}']*len(row)
    st.dataframe(st.session_state.matriz_riesgos.style.apply(color_fila, axis=1))
else:
    st.info(txt["info_agrega_riesgos_matriz"])
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

if "matriz_riesgos" in st.session_state and not st.session_state.matriz_riesgos.empty:
    st.markdown(f"## {txt['mapa_calor_titulo']}")

    # Preparar matriz para heatmap: promedio Riesgo Residual por Tipo Impacto y Nivel Probabilidad
    matriz_calor = st.session_state.matriz_riesgos.pivot_table(
        index="Tipo Impacto",
        columns="Nivel Probabilidad",
        values="Riesgo Residual",
        aggfunc=np.mean,
        fill_value=0
    )

    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(matriz_calor, annot=True, fmt=".2f", cmap="RdYlGn_r", ax=ax)
    ax.set_xlabel(txt["factor_probabilidad_titulo"])
    ax.set_ylabel(txt["tipo_impacto_titulo"])
    st.pyplot(fig)

    # Gráfico de Pareto de Riesgos
    df_pareto = st.session_state.matriz_riesgos.copy()
    df_pareto = df_pareto.sort_values(by="Riesgo Residual", ascending=False)
    df_pareto["% Riesgo"] = 100 * df_pareto["Riesgo Residual"] / df_pareto["Riesgo Residual"].sum()
    df_pareto["% Acumulado"] = df_pareto["% Riesgo"].cumsum()

    fig2, ax1 = plt.subplots(figsize=(10,4))

    ax1.bar(df_pareto["Nombre Riesgo"], df_pareto["% Riesgo"], color='skyblue')
    ax1.set_ylabel("% Riesgo Individual" if lang=="es" else "% Individual Risk", color='blue')
    ax1.set_xticklabels(df_pareto["Nombre Riesgo"], rotation=45, ha='right')

    ax2 = ax1.twinx()
    ax2.plot(df_pareto["Nombre Riesgo"], df_pareto["% Acumulado"], color='red', marker='o')
    ax2.set_ylabel("% Riesgo Acumulado" if lang=="es" else "% Cumulative Risk", color='red')
    ax2.axhline(80, color='gray', linestyle='dashed')
    ax2.text(len(df_pareto)*0.7, 82, "80% Línea de Pareto" if lang=="es" else "80% Pareto Line", color='gray')

    ax1.set_title("Gráfico de Pareto de Riesgos" if lang=="es" else "Risk Pareto Chart")
    plt.tight_layout()
    st.pyplot(fig2)
else:
    st.info(txt["info_agrega_riesgos"])
from io import BytesIO

if "matriz_riesgos" in st.session_state and not st.session_state.matriz_riesgos.empty:
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.matriz_riesgos.to_excel(writer, index=False, sheet_name="Matriz de Riesgos")
        writer.save()
    st.download_button(
        label=txt["descargar_excel"],
        data=output.getvalue(),
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info(txt["info_agrega_riesgos_matriz"])

