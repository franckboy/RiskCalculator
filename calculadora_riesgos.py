import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

# Textos en ambos idiomas
textos = {
    "es": {
        "idioma_espanol": "Español",
        "idioma_ingles": "Inglés",
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
        "amenaza_deliberada_opciones": {1:"Baja", 2:"Intermedia", 3:"Alta"},
        "efectividad_control": "Efectividad del control (%)",
        "impacto": "Impacto",
        "resultados": "Resultados",
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
        "descargar_excel": "Descargar matriz de riesgos en Excel",
        "info_agrega_riesgos_matriz": "Agrega riesgos para mostrar la matriz acumulativa."
    },
    "en": {
        "idioma_espanol": "Spanish",
        "idioma_ingles": "English",
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
        "nombre_riesgo": "Risk Name",
        "descripcion_riesgo": "Risk Description",
        "tipo_impacto": "Impact Type",
        "justificacion": "Justification",
        "factor_exposicion": "Exposure Factor",
        "factor_probabilidad": "Probability Factor",
        "amenaza_deliberada": "Deliberate Threat",
        "amenaza_deliberada_opciones": {1:"Low", 2:"Medium", 3:"High"},
        "efectividad_control": "Control Effectiveness (%)",
        "impacto": "Impact",
        "resultados": "Results",
        "amenaza_inherente": "Inherent Threat",
        "amenaza_residual": "Residual Threat",
        "amenaza_residual_ajustada": "Adjusted Residual Threat (x Deliberate Threat)",
        "riesgo_residual": "Residual Risk",
        "clasificacion": "Classification",
        "agregar_riesgo": "Add risk to matrix",
        "exito_agregar": "Risk added to cumulative matrix.",
        "mapa_calor_titulo": "Heatmap by Impact Type and Probability vs Impact",
        "info_agrega_riesgos": "Add risks to display the heatmap.",
        "matriz_acumulativa_titulo": "Cumulative Risk Matrix",
        "descargar_excel": "Download risk matrix in Excel",
        "info_agrega_riesgos_matriz": "Add risks to display the cumulative matrix."
    }
}

# Datos de tablas con columnas fijas en español
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
        "Directly affects life, health or integrity of people. Highest priority per ISO 45001.",
        "Ecological damage can be irreversible and carry severe sanctions. ISO 14001.",
        "Financial losses affect business continuity and viability. COSO ERM.",
        "Disrupts critical processes, production or key services. ISO 22301.",
        "Physical damage to facilities or assets affects operations and safety.",
        "System failures or cyberattacks affect data and processes. ISO 27005.",
        "Affects public image, trust and may lead to indirect sanctions. COSO ERM.",
        "Impacts communities, labor conditions or social responsibility. ISO 26000.",
        "Loss of customers, contracts or market. Recoverable but affects income."
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
        "Robust and well-implemented control.",
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
        "Exposure several times a year",
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
        "Likely on occasions",
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
        "No significant effect",
        "Minor effect",
        "Partial and temporary effect",
        "Significant effect",
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

# Selector idioma en barra lateral con expander y valor por defecto
idioma = "es"  # por defecto

with st.sidebar.expander("🌐 Language / Idioma", expanded=True):
    idioma = st.radio(
        label="Select Language / Seleccionar idioma",
        options=["es", "en"],
        format_func=lambda x: textos[x]["idioma_espanol"] if x == "es" else textos[x]["idioma_ingles"]
    )

# Asignar tablas según idioma para mostrar
if idioma == "es":
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto.rename(columns={
        "Código": "Código", "Tipo de Impacto": "Tipo de Impacto", "Ponderación": "Ponderación", "Justificación": "Justificación"
    })
    tabla_efectividad_mostrar = tabla_efectividad.rename(columns={
        "Rango": "Rango", "Mitigacion": "Mitigacion", "Descripcion": "Descripcion"
    })
    tabla_exposicion_mostrar = tabla_exposicion.rename(columns={
        "Factor": "Factor", "Nivel": "Nivel", "Descripcion": "Descripcion"
    })
    tabla_probabilidad_mostrar = tabla_probabilidad.rename(columns={
        "Factor": "Factor", "Nivel": "Nivel", "Descripcion": "Descripcion"
    })
    tabla_impacto_mostrar = tabla_impacto.rename(columns={
        "Nivel": "Nivel", "Valor": "Valor", "Descripcion": "Descripcion"
    })
    tabla_criticidad_mostrar = tabla_criticidad.rename(columns={
        "Límite Superior": "Límite Superior", "Clasificación": "Clasificación", "Color": "Color"
    })
    clasificar_criticidad_usar = clasificar_criticidad
else:
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto_en.rename(columns={
        "Code": "Code", "Impact Type": "Impact Type", "Weighting": "Weighting", "Justification": "Justification"
    })
    tabla_efectividad_mostrar = tabla_efectividad_en.rename(columns={
        "Range": "Range", "Mitigation": "Mitigation", "Description": "Description"
    })
    tabla_exposicion_mostrar = tabla_exposicion_en.rename(columns={
        "Factor": "Factor", "Level": "Level", "Description": "Description"
    })
    tabla_probabilidad_mostrar = tabla_probabilidad_en.rename(columns={
        "Factor": "Factor", "Level": "Level", "Description": "Description"
    })
    tabla_impacto_mostrar = tabla_impacto_en.rename(columns={
        "Level": "Level", "Value": "Value", "Description": "Description"
    })
    tabla_criticidad_mostrar = tabla_criticidad_en.rename(columns={
        "Upper Limit": "Upper Limit", "Classification": "Classification", "Color": "Color"
    })
    clasificar_criticidad_usar = clasificar_criticidad_en

# Layout principal
col_izq, col_centro, col_der = st.columns([1.3, 2, 2])

with col_izq:
    mostrar_tabla_fija(tabla_efectividad_mostrar, textos[idioma]["factor_exposicion_titulo"])
    mostrar_tabla_fija(tabla_exposicion_mostrar, textos[idioma]["factor_probabilidad_titulo"])
    mostrar_tabla_fija(tabla_probabilidad_mostrar, textos[idioma]["impacto_severidad_titulo"])
    mostrar_tabla_fija(tabla_tipo_impacto_mostrar, textos[idioma]["tipo_impacto_titulo"])
    st.markdown(f"### {textos[idioma]['indice_criticidad_titulo']}")
    crit_display = tabla_criticidad_mostrar.drop(columns=["Color"])
    st.table(crit_display)
    st.markdown(textos[idioma]["indice_criticidad_descripcion"], unsafe_allow_html=True)

with col_centro:
    st.title("Calculadora de Riesgos" if idioma=="es" else "Risk Calculator")
    st.subheader(textos[idioma]["resultados"])

    nombre_riesgo = st.text_input(textos[idioma]["nombre_riesgo"])
    descripcion = st.text_area(textos[idioma]["descripcion_riesgo"])

    opciones_impacto_visibles = tabla_tipo_impacto_mostrar.apply(
        lambda row: f"{row.iloc[0]} - {row.iloc[1]}", axis=1).tolist()
    seleccion_impacto = st.selectbox(textos[idioma]["tipo_impacto"], opciones_impacto_visibles)
    codigo_impacto = seleccion_impacto.split(" - ")[0]

    if idioma == "es":
        justificacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Justificación"].values[0]
        ponderacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Ponderación"].values[0]
    else:
        justificacion_impacto = tabla_tipo_impacto_en.loc[tabla_tipo_impacto_en["Code"] == codigo_impacto, "Justification"].values[0]
        ponderacion_impacto = tabla_tipo_impacto_en.loc[tabla_tipo_impacto_en["Code"] == codigo_impacto, "Weighting"].values[0]

    st.markdown(f"**{textos[idioma]['justificacion']}:** {justificacion_impacto}")

    exposicion = st.selectbox(
        textos[idioma]["factor_exposicion"],
        options=tabla_exposicion["Factor"],
        format_func=lambda x: (
            f"{x} - {tabla_exposicion['Nivel'].values[tabla_exposicion['Factor'].tolist().index(x)]}"
            if idioma=="es"
            else f"{x} - {tabla_exposicion_en['Level'].values[tabla_exposicion_en['Factor'].tolist().index(x)]}"
        )
    )
    probabilidad = st.selectbox(
        textos[idioma]["factor_probabilidad"],
        options=tabla_probabilidad["Factor"],
        format_func=lambda x: (
            f"{x} - {tabla_probabilidad['Nivel'].values[tabla_probabilidad['Factor'].tolist().index(x)]}"
            if idioma=="es"
            else f"{x} - {tabla_probabilidad_en['Level'].values[tabla_probabilidad_en['Factor'].tolist().index(x)]}"
        )
    )
    amenaza_deliberada = st.selectbox(
        textos[idioma]["amenaza_deliberada"],
        options=[1, 2, 3],
        format_func=lambda x: textos[idioma]["amenaza_deliberada_opciones"][x],
        index=0
    )
    efectividad = st.slider(textos[idioma]["efectividad_control"], 0, 100, 50)

    impacto = st.selectbox(
        textos[idioma]["impacto"],
        options=tabla_impacto["Nivel"],
        format_func=lambda x: (
            f"{x} - {tabla_impacto['Descripcion'].values[tabla_impacto['Nivel'].tolist().index(x)]}"
            if idioma=="es"
            else f"{x} - {tabla_impacto_en['Description'].values[tabla_impacto_en['Level'].tolist().index(x)]}"
        )
    )

    efectividad_norm = efectividad / 100
    valor_impacto = tabla_impacto.loc[tabla_impacto["Nivel"] == impacto, "Valor"].values[0]

    amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual = calcular_criticidad(
        probabilidad, exposicion, amenaza_deliberada, efectividad_norm, valor_impacto, ponderacion_impacto
    )

    clasificacion, color = clasificar_criticidad_usar(riesgo_residual)

    st.markdown(f"### {textos[idioma]['resultados']}:")
    st.write(f"- {textos[idioma]['amenaza_inherente']}: {amenaza_inherente:.4f}")
    st.write(f"- {textos[idioma]['amenaza_residual']}: {amenaza_residual:.4f}")
    st.write(f"- {textos[idioma]['amenaza_residual_ajustada']}: {amenaza_residual_ajustada:.4f}")
    st.write(f"- {textos[idioma]['riesgo_residual']}: {riesgo_residual:.4f}")
    st.write(f"- {textos[idioma]['clasificacion']}: **{clasificacion}** (Color: {color})")

    if st.button(textos[idioma]["agregar_riesgo"]) and nombre_riesgo.strip() != "":
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
        st.success(textos[idioma]["exito_agregar"])

with col_der:
    st.header(textos[idioma]["mapa_calor_titulo"])

    if not st.session_state.riesgos.empty:
        st.session_state.riesgos["Valor Mapa"] = (
            st.session_state.riesgos["Amenaza Residual"] *  # Aquí se usa Amenaza Residual, no Inherente
            st.session_state.riesgos["Impacto"].map(
                lambda x: tabla_impacto.loc[tabla_impacto["Nivel"] == x, "Valor"].values[0]
            )
        )

        matriz_calor = st.session_state.riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Probabilidad",
            values="Valor Mapa",
            aggfunc=np.mean
        ).fillna(0).sort_index()

        fig, ax = plt.subplots(figsize=(7,5))
        sns.heatmap(
            matriz_calor,
            annot=True,
            fmt=".2f",
            cmap=cmap,
            cbar_kws={"label": f"{textos[idioma]['amenaza_residual']} × {textos[idioma]['impacto']}"}
        )
        ax.set_xlabel(textos[idioma]["factor_probabilidad"])
        ax.set_ylabel(textos[idioma]["tipo_impacto_titulo"])
        st.pyplot(fig)
    else:
        st.info(textos[idioma]["info_agrega_riesgos"])

st.markdown("---")
st.header(textos[idioma]["matriz_acumulativa_titulo"])

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
        st.session_state.riesgos.to_excel(writer, index=False, sheet_name="Riesgos")
    processed_data = output.getvalue()

    st.download_button(
        label=textos[idioma]["descargar_excel"],
        data=processed_data,
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info(textos[idioma]["info_agrega_riesgos_matriz"])
