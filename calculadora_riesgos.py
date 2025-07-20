import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

# Diccionario de textos para español e inglés
textos = {
    "es": {
        "efectividad_controles_titulo": "Efectividad de Controles",
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
        "resultados": "Resultados:",
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
        "descargar_excel": "Descargar matriz de riesgos en Excel",
        "idioma_selector_titulo": "Selecciona idioma",
        "idioma_espanol": "Español",
        "idioma_ingles": "English",
        "mostrar_selector": "Mostrar selector de idioma"
    },
    "en": {
        "efectividad_controles_titulo": "Control Effectiveness",
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
                <li style='color:red;'>Red: Intolerable (> 15)</li>
            </ul>
        """,
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
        "resultados": "Results:",
        "amenaza_inherente": "Inherent Threat",
        "amenaza_residual": "Residual Threat",
        "amenaza_residual_ajustada": "Adjusted Residual Threat (x Deliberate Threat)",
        "riesgo_residual": "Residual Risk",
        "clasificacion": "Classification",
        "agregar_riesgo": "Add Risk to Matrix",
        "exito_agregar": "Risk added to the cumulative matrix.",
        "mapa_calor_titulo": "Heatmap by Impact Type and Probability vs Impact",
        "info_agrega_riesgos": "Add risks to display the heatmap.",
        "matriz_acumulativa_titulo": "Cumulative Risk Matrix",
        "info_agrega_riesgos_matriz": "Add risks to display the cumulative matrix.",
        "descargar_excel": "Download risk matrix as Excel",
        "idioma_selector_titulo": "Select Language",
        "idioma_espanol": "Spanish",
        "idioma_ingles": "English",
        "mostrar_selector": "Show language selector"
    }
}

# Sidebar para idioma, puede esconderse
with st.sidebar.expander("🌐 Language / Idioma", expanded=True):
    idioma = st.radio(
        label="Select Language / Seleccionar idioma",
        options=["es", "en"],
        format_func=lambda x: textos[x]["idioma_espanol"] if x=="es" else textos[x]["idioma_ingles"]
    )
else:
    # Default por si no está seleccionado
    idioma = "es"

t = textos[idioma]  # Diccionario actual para texto

# --- Tablas traducidas (misma estructura, solo nombres columnas y textos) ---

tabla_tipo_impacto = pd.DataFrame({
    t["tipo_impacto"].split()[0]: ["H", "A", "E", "O", "I", "T", "R", "S", "C"],
    t["tipo_impacto"]: [
        t["idioma_espanol"] if idioma=="es" else "Human",
        "Ambiental" if idioma=="es" else "Environmental",
        "Económico" if idioma=="es" else "Economic",
        "Operacional" if idioma=="es" else "Operational",
        "Infraestructura" if idioma=="es" else "Infrastructure",
        "Tecnológico" if idioma=="es" else "Technological",
        "Reputacional" if idioma=="es" else "Reputational",
        "Social" if idioma=="es" else "Social",
        "Comercial" if idioma=="es" else "Commercial",
    ],
    "Ponderación" if idioma=="es" else "Weighting": [100, 85, 80, 75, 65, 60, 50, 45, 40],
    "Justificación" if idioma=="es" else "Justification": [
        "Afecta directamente la vida, salud o integridad de las personas. Prioridad máxima según ISO 45001."
        if idioma=="es"
        else "Directly affects life, health or integrity of people. Highest priority per ISO 45001.",
        "Daños ecológicos pueden ser irreversibles y conllevan sanciones graves. ISO 14001."
        if idioma=="es"
        else "Ecological damage can be irreversible with severe penalties. ISO 14001.",
        "Pérdidas financieras afectan continuidad y viabilidad del negocio. COSO ERM."
        if idioma=="es"
        else "Financial losses affect continuity and viability of business. COSO ERM.",
        "Interrumpe procesos críticos, producción o servicios clave. ISO 22301."
        if idioma=="es"
        else "Interrupts critical processes, key production or services. ISO 22301.",
        "Daño físico a instalaciones o activos afecta operaciones y seguridad."
        if idioma=="es"
        else "Physical damage to facilities or assets affects operations and safety.",
        "Fallas de sistemas o ciberataques afectan datos y procesos. ISO 27005."
        if idioma=="es"
        else "System failures or cyberattacks affect data and processes. ISO 27005.",
        "Afecta imagen pública, confianza y puede derivar en sanciones indirectas. COSO ERM."
        if idioma=="es"
        else "Affects public image, trust and may cause indirect sanctions. COSO ERM.",
        "Impacta comunidades, condiciones laborales o responsabilidad social. ISO 26000."
        if idioma=="es"
        else "Impacts communities, working conditions, or social responsibility. ISO 26000.",
        "Pérdida de clientes, contratos o mercado. Es recuperable pero afecta ingresos."
        if idioma=="es"
        else "Loss of clients, contracts or market. Recoverable but affects revenue."
    ]
})

tabla_efectividad = pd.DataFrame({
    "Rango" if idioma=="es" else "Range": ["0%", "1 - 20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
    "Factor": [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.1],
    "Mitigacion" if idioma=="es" else "Mitigation": [
        "Inefectiva" if idioma=="es" else "Ineffective",
        "Limitada" if idioma=="es" else "Limited",
        "Baja" if idioma=="es" else "Low",
        "Intermedia" if idioma=="es" else "Intermediate",
        "Alta" if idioma=="es" else "High",
        "Muy alta" if idioma=="es" else "Very High",
        "Total" if idioma=="es" else "Total"
    ],
    "Descripcion" if idioma=="es" else "Description": [
        "No reduce el riesgo" if idioma=="es" else "Does not reduce risk",
        "Reduce solo en condiciones ideales" if idioma=="es" else "Reduces risk only in ideal cases",
        "Mitiga riesgos menores." if idioma=="es" else "Mitigates minor risks",
        "Control estándar con limitaciones." if idioma=="es" else "Standard control with limitations",
        "Reduce significativamente el riesgo" if idioma=="es" else "Significantly reduces risk",
        "Control robusto y bien implementado." if idioma=="es" else "Robust and well implemented control",
        "Elimina casi todo el riesgo" if idioma=="es" else "Eliminates nearly all risk"
    ]
})

tabla_exposicion = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel" if idioma=="es" else "Level": [
        "Muy Baja" if idioma=="es" else "Very Low",
        "Baja" if idioma=="es" else "Low",
        "Moderada" if idioma=="es" else "Moderate",
        "Alta" if idioma=="es" else "High",
        "Muy Alta" if idioma=="es" else "Very High",
    ],
    "Descripcion" if idioma=="es" else "Description": [
        "Exposición extremadamente rara" if idioma=="es" else "Extremely rare exposure",
        "Exposición ocasional (cada 10 años)" if idioma=="es" else "Occasional exposure (every 10 years)",
        "Exposición algunas veces al año" if idioma=="es" else "Exposure several times per year",
        "Exposición mensual" if idioma=="es" else "Monthly exposure",
        "Exposición frecuente o semanal" if idioma=="es" else "Frequent or weekly exposure"
    ]
})

tabla_probabilidad = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel" if idioma=="es" else "Level": [
        "Muy Baja" if idioma=="es" else "Very Low",
        "Baja" if idioma=="es" else "Low",
        "Moderada" if idioma=="es" else "Moderate",
        "Alta" if idioma=="es" else "High",
        "Muy Alta" if idioma=="es" else "Very High",
    ],
    "Descripcion" if idioma=="es" else "Description": [
        "En condiciones excepcionales" if idioma=="es" else "Under exceptional conditions",
        "Ha sucedido alguna vez" if idioma=="es" else "Has occurred once",
        "Podría ocurrir ocasionalmente" if idioma=="es" else "Could occur occasionally",
        "Probable en ocasiones" if idioma=="es" else "Probable sometimes",
        "Ocurre con frecuencia / inminente" if idioma=="es" else "Occurs frequently/imminent"
    ]
})

tabla_impacto = pd.DataFrame({
    "Nivel" if idioma=="es" else "Level": [1, 2, 3, 4, 5],
    "Valor" if idioma=="es" else "Value": [5, 10, 30, 60, 85],
    "Descripcion" if idioma=="es" else "Description": [
        "No afecta significativamente" if idioma=="es" else "Does not significantly affect",
        "Afectación menor" if idioma=="es" else "Minor effect",
        "Afectación parcial y temporal" if idioma=="es" else "Partial and temporary effect",
        "Afectación significativa" if idioma=="es" else "Significant effect",
        "Impacto serio o pérdida total" if idioma=="es" else "Serious impact or total loss"
    ]
})

tabla_criticidad = pd.DataFrame({
    "Límite Superior" if idioma=="es" else "Upper Limit": [2, 4, 15, float('inf')],
    "Clasificación" if idioma=="es" else "Classification": ["ACEPTABLE", "TOLERABLE", "INACEPTABLE", "INADMISIBLE"] if idioma=="es" else ["ACCEPTABLE", "TOLERABLE", "UNACCEPTABLE", "INTOLERABLE"],
    "Color": ["Verde", "Amarillo", "Naranja", "Rojo"] if idioma=="es" else ["Green", "Yellow", "Orange", "Red"]
})

colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]
cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

def clasificar_criticidad(valor):
    if valor <= 2:
        return t["indice_criticidad_descripcion"].split(">")[1].strip().split()[0] if idioma=="en" else "ACEPTABLE", colors[0] if idioma=="es" else "Green"
    elif valor <= 4:
        return t["indice_criticidad_descripcion"].split(">")[2].strip().split()[0] if idioma=="en" else "TOLERABLE", colors[1] if idioma=="es" else "Yellow"
    elif valor <= 15:
        return t["indice_criticidad_descripcion"].split(">")[3].strip().split()[0] if idioma=="en" else "INACEPTABLE", colors[2] if idioma=="es" else "Orange"
    else:
        return t["indice_criticidad_descripcion"].split(">")[4].strip().split()[0] if idioma=="en" else "INADMISIBLE", colors[3] if idioma=="es" else "Red"

def mostrar_tabla_fija(df, titulo):
    st.markdown(f"### {titulo}")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True, filter=False, sortable=False)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, height=min(200, 35*len(df)), fit_columns_on_grid_load=True, enable_enterprise_modules=False, update_mode='NO_UPDATE')

def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto):
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        t["nombre_riesgo"], t["descripcion_riesgo"], t["tipo_impacto"], t["factor_exposicion"], t["factor_probabilidad"], t["amenaza_deliberada"],
        t["efectividad_control"], t["impacto"], t["amenaza_inherente"], t["amenaza_residual"], t["amenaza_residual_ajustada"],
        t["riesgo_residual"], t["clasificacion"], "Color " + t["clasificacion"]
    ])

# Layout principal
col_izq, col_centro, col_der = st.columns([1.3, 2, 2])

with col_izq:
    mostrar_tabla_fija(tabla_efectividad[[("Rango" if idioma=="es" else "Range"), ("Mitigacion" if idioma=="es" else "Mitigation"), ("Descripcion" if idioma=="es" else "Description")]], t["efectividad_controles_titulo"])
    mostrar_tabla_fija(tabla_exposicion[[ "Factor", ("Nivel" if idioma=="es" else "Level"), ("Descripcion" if idioma=="es" else "Description")]], t["factor_exposicion_titulo"])
    mostrar_tabla_fija(tabla_probabilidad[[ "Factor", ("Nivel" if idioma=="es" else "Level"), ("Descripcion" if idioma=="es" else "Description")]], t["factor_probabilidad_titulo"])
    mostrar_tabla_fija(tabla_impacto[[("Nivel" if idioma=="es" else "Level"), ("Valor" if idioma=="es" else "Value"), ("Descripcion" if idioma=="es" else "Description")]], t["impacto_severidad_titulo"])
    mostrar_tabla_fija(tabla_tipo_impacto, t["tipo_impacto_titulo"])
    st.markdown(f"### {t['indice_criticidad_titulo']}")
    crit_display = tabla_criticidad.drop(columns=["Color"])
    st.table(crit_display)
    st.markdown(t["indice_criticidad_descripcion"], unsafe_allow_html=True)

with col_centro:
    st.title("Calculadora de Riesgos" if idioma=="es" else "Risk Calculator")
    st.subheader(t["resultados"])

    nombre_riesgo = st.text_input(t["nombre_riesgo"])
    descripcion = st.text_area(t["descripcion_riesgo"])

    opciones_impacto_visibles = tabla_tipo_impacto.apply(
        lambda row: f"{row[t['tipo_impacto'].split()[0]]} - {row[t['tipo_impacto']]}", axis=1).tolist()
    seleccion_impacto = st.selectbox(t["tipo_impacto"], opciones_impacto_visibles)
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    justificacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto[t['tipo_impacto'].split()[0]] == codigo_impacto, "Justificación" if idioma=="es" else "Justification"].values[0]
    ponderacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto[t['tipo_impacto'].split()[0]] == codigo_impacto, "Ponderación" if idioma=="es" else "Weighting"].values[0]
    st.markdown(f"**{t['justificacion']}:** {justificacion_impacto}")

    exposicion = st.selectbox(
        t["factor_exposicion"],
        options=tabla_exposicion["Factor"],
        format_func=lambda x: f"{x} - {tabla_exposicion.loc[tabla_exposicion['Factor']==x, 'Nivel' if idioma=="es" else 'Level'].values[0]}"
    )
    probabilidad = st.selectbox(
        t["factor_probabilidad"],
        options=tabla_probabilidad["Factor"],
        format_func=lambda x: f"{x} - {tabla_probabilidad.loc[tabla_probabilidad['Factor']==x, 'Nivel' if idioma=="es" else 'Level'].values[0]}"
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
        options=tabla_impacto["Nivel" if idioma=="es" else "Level"],
        format_func=lambda x: f"{x} - {tabla_impacto.loc[tabla_impacto['Nivel' if idioma=="es" else "Level"]==x, 'Descripcion' if idioma=="es" else 'Description'].values[0]}"
    )

    efectividad_norm = efectividad / 100
    valor_impacto = tabla_impacto.loc[tabla_impacto["Nivel" if idioma=="es" else "Level"] == impacto, "Valor" if idioma=="es" else "Value"].values[0]

    amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual = calcular_criticidad(
        probabilidad, exposicion, amenaza_deliberada, efectividad_norm, valor_impacto, ponderacion_impacto
    )

    clasificacion, color = clasificar_criticidad(riesgo_residual)

    st.markdown(f"### {t['resultados']}")
    st.write(f"- {t['amenaza_inherente']}: {amenaza_inherente:.4f}")
    st.write(f"- {t['amenaza_residual']}: {amenaza_residual:.4f}")
    st.write(f"- {t['amenaza_residual_ajustada']}: {amenaza_residual_ajustada:.4f}")
    st.write(f"- {t['riesgo_residual']}: {riesgo_residual:.4f}")
    st.write(f"- {t['clasificacion']}: **{clasificacion}** (Color: {color})")

    if st.button(t["agregar_riesgo"]) and nombre_riesgo.strip() != "":
        nuevo_riesgo = {
            t["nombre_riesgo"]: nombre_riesgo.strip(),
            t["descripcion_riesgo"]: descripcion.strip(),
            t["tipo_impacto"]: codigo_impacto,
            t["factor_exposicion"]: exposicion,
            t["factor_probabilidad"]: probabilidad,
            t["amenaza_deliberada"]: amenaza_deliberada,
            t["efectividad_control"]: efectividad,
            t["impacto"]: impacto,
            t["amenaza_inherente"]: amenaza_inherente,
            t["amenaza_residual"]: amenaza_residual,
            t["amenaza_residual_ajustada"]: amenaza_residual_ajustada,
            t["riesgo_residual"]: riesgo_residual,
            t["clasificacion"]: clasificacion,
            "Color " + t["clasificacion"]: color
        }
        st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
        st.success(t["exito_agregar"])

with col_der:
    st.header(t["mapa_calor_titulo"])

    if not st.session_state.riesgos.empty:
        # Valor para el mapa = Amenaza Residual Ajustada * Valor Impacto
        st.session_state.riesgos["Valor Mapa"] = (
            st.session_state.riesgos[t["amenaza_residual_ajustada"]] *
            st.session_state.riesgos[t["impacto"]].map(
                lambda x: tabla_impacto.loc[tabla_impacto["Nivel" if idioma=="es" else "Level"] == x, "Valor" if idioma=="es" else "Value"].values[0]
            )
        )

        matriz_calor = st.session_state.riesgos.pivot_table(
            index=t["tipo_impacto"],
            columns=t["factor_probabilidad"],
            values="Valor Mapa",
            aggfunc=np.mean
        ).fillna(0).sort_index()

        fig, ax = plt.subplots(figsize=(7,5))
        sns.heatmap(
            matriz_calor,
            annot=True,
            fmt=".2f",
            cmap=cmap,
            cbar_kws={"label": "Amenaza Residual Ajustada × Impacto" if idioma=="es" else "Adjusted Residual Threat × Impact"}
        )
        ax.set_xlabel(t["factor_probabilidad"])
        ax.set_ylabel(t["tipo_impacto"])
        st.pyplot(fig)
    else:
        st.info(t["info_agrega_riesgos"])

st.markdown("---")
st.header(t["matriz_acumulativa_titulo"])
if not st.session_state.riesgos.empty:
    gb = GridOptionsBuilder.from_dataframe(st.session_state.riesgos)
    gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True)
    gb.configure_pagination(enabled=True)
    gridOptions = gb.build()
    AgGrid(
        st.session_state.riesgos,
        gridOptions=gridOptions,
        height=400,
        fit_columns_on_grid_load=True
    )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        st.session_state.riesgos.to_excel(writer, index=False, sheet_name="Riesgos" if idioma=="es" else "Risks")
        # No hace falta writer.save() al usar contexto with
    processed_data = output.getvalue()

    st.download_button(
        label=t["descargar_excel"],
        data=processed_data,
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info(t["info_agrega_riesgos_matriz"])

