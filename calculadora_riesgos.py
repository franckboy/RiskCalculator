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

# Tablas fijas traducidas (solo lo necesario para listas)
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

tabla_criticidad = pd.DataFrame({
    "Límite Superior": [0.7, 3, 7, float('inf')],
    "Clasificación": ["ACEPTABLE", "TOLERABLE", "INACEPTABLE", "INADMISIBLE"],
    "Color": ["Verde", "Amarillo", "Naranja", "Rojo"]
})

colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]
cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

def clasificar_criticidad(valor):
    if valor <= 0.7:
        return "ACEPTABLE", "Verde"
    elif valor <= 3:
        return "TOLERABLE", "Amarillo"
    elif valor <= 7:
        return "INACEPTABLE", "Naranja"
    else:
        return "INADMISIBLE", "Rojo"

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

# Selector idioma en sidebar
with st.sidebar.expander("Language / Idioma", expanded=True):
    idioma = st.selectbox("Selecciona idioma / Select language", options=["es", "en"], index=0)

# Variables para tablas y funciones según idioma
if idioma == "es":
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto
    tabla_exposicion_mostrar = tabla_exposicion
    tabla_probabilidad_mostrar = tabla_probabilidad
    tabla_impacto_mostrar = tabla_impacto
    clasificar_criticidad_usar = clasificar_criticidad
else:
    st.error("Idioma inglés no implementado en este ejemplo para mantener simplicidad.")
    st.stop()

# Layout principal
col_izq, col_centro, col_der = st.columns([1, 2, 2])

with col_izq:
    # No mostrar tablas fijas, solo etiquetas y explicación
    st.markdown(f"### {textos[idioma]['indice_criticidad_titulo']}")
    crit_display = tabla_criticidad[["Límite Superior", "Clasificación"]].rename(
        columns={"Límite Superior": "Límite Superior", "Clasificación": "Clasificación"}
    )
    st.table(crit_display.style.applymap(
        lambda v: f"background-color: { 'green' if v=='ACEPTABLE' else 'yellow' if v=='TOLERABLE' else 'orange' if v=='INACEPTABLE' else 'red' }", subset=["Clasificación"]
    ))
    st.markdown(textos[idioma]["indice_criticidad_descripcion"], unsafe_allow_html=True)

with col_centro:
    st.title("Calculadora de Riesgos")
    st.subheader(textos[idioma]["resultados"])

    nombre_riesgo = st.text_input(textos[idioma]["nombre_riesgo"])
    descripcion = st.text_area(textos[idioma]["descripcion_riesgo"])

    opciones_impacto_visibles = tabla_tipo_impacto_mostrar.apply(
        lambda row: f"{row['Código']} - {row['Tipo de Impacto']}", axis=1).tolist()
    seleccion_impacto = st.selectbox(textos[idioma]["tipo_impacto"], opciones_impacto_visibles)
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    justificacion_impacto = tabla_tipo_impacto_mostrar.loc[tabla_tipo_impacto_mostrar["Código"] == codigo_impacto, "Justificación"].values[0]
    ponderacion_impacto = tabla_tipo_impacto_mostrar.loc[tabla_tipo_impacto_mostrar["Código"] == codigo_impacto, "Ponderación"].values[0]
    st.markdown(f"**{textos[idioma]['justificacion']}:** {justificacion_impacto}")

    exposicion = st.selectbox(
        textos[idioma]["factor_exposicion"],
        options=tabla_exposicion_mostrar["Factor"],
        format_func=lambda x: f"{x} - {tabla_exposicion_mostrar.loc[tabla_exposicion_mostrar['Factor'] == x, 'Nivel'].values[0]}"
    )

    probabilidad = st.selectbox(
        textos[idioma]["factor_probabilidad"],
        options=tabla_probabilidad_mostrar["Factor"],
        format_func=lambda x: f"{x} - {tabla_probabilidad_mostrar.loc[tabla_probabilidad_mostrar['Factor'] == x, 'Nivel'].values[0]}"
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
        options=tabla_impacto_mostrar["Nivel"],
        format_func=lambda x: f"{x} - {tabla_impacto_mostrar.loc[tabla_impacto_mostrar['Nivel'] == x, 'Descripcion'].values[0]}"
    )

    efectividad_norm = efectividad / 100
    valor_impacto = tabla_impacto_mostrar.loc[tabla_impacto_mostrar["Nivel"] == impacto, "Valor"].values[0]

    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad_norm)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)

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

    explicacion_probabilidad = {
        "es": """
        **Probabilidad Residual (Amenaza Residual) = Amenaza Inherente × (1 - Efectividad Control)**

        En el mapa de calor, la probabilidad se calcula como la probabilidad residual después de aplicar los controles, y el impacto es el valor que el usuario elige para cada riesgo.
        """
    }
    st.markdown(explicacion_probabilidad[idioma])

    if not st.session_state.riesgos.empty:
        st.session_state.riesgos["Valor Mapa"] = (
            st.session_state.riesgos["Amenaza Residual"] *
            st.session_state.riesgos["Impacto"].map(
                lambda x: tabla_impacto_mostrar.loc[tabla_impacto_mostrar["Nivel"] == x, "Valor"].values[0]
            )
        )

        matriz_calor = st.session_state.riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Probabilidad",
            values="Valor Mapa",
            aggfunc=np.mean
        ).fillna(0).sort_index()

        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(
            matriz_calor,
            annot=True,
            fmt=".2f",
            cmap=cmap,
            cbar_kws={"label": textos[idioma]["mapa_calor_titulo"]}
        )
        ax.set_xlabel(textos[idioma]["factor_probabilidad_titulo"])
        ax.set_ylabel(textos[idioma]["tipo_impacto_titulo"])
        st.pyplot(fig)

        # Gráfico Pareto de riesgos
        df_pareto = st.session_state.riesgos.copy()
        df_pareto = df_pareto.sort_values(by="Riesgo Residual", ascending=False)
        df_pareto["% Riesgo"] = 100 * df_pareto["Riesgo Residual"] / df_pareto["Riesgo Residual"].sum()
        df_pareto["% Acumulado"] = df_pareto["% Riesgo"].cumsum()

        fig2, ax1 = plt.subplots(figsize=(7, 5))
        ax2 = ax1.twinx()
        ax1.bar(df_pareto["Nombre Riesgo"], df_pareto["% Riesgo"], color="C0")
        ax2.plot(df_pareto["Nombre Riesgo"], df_pareto["% Acumulado"], color="C1", marker="D", ms=5)
        ax1.set_ylabel("% Riesgo")
        ax2.set_ylabel("% Acumulado")
        ax1.set_xticklabels(df_pareto["Nombre Riesgo"], rotation=45, ha="right")
        st.pyplot(fig2)

        # Matriz acumulativa de riesgos
        st.subheader(textos[idioma]["matriz_acumulativa_titulo"])
        matriz_acum = st.session_state.riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Nombre Riesgo",
            values="Riesgo Residual",
            aggfunc=np.sum,
            fill_value=0
        )
        st.dataframe(matriz_acum)

        # Botón para exportar Excel
        def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=True, sheet_name='Matriz_Riesgos')
    processed_data = output.getvalue()
    return processed_data

        df_export = st.session_state.riesgos.drop(columns=["Color Criticidad"])

        excel_data = to_excel(df_export)
        st.download_button(
            label=textos[idioma]["descargar_excel"],
            data=excel_data,
            file_name='matriz_riesgos.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    else:
        st.info(textos[idioma]["info_agrega_riesgos"])


  
