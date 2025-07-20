import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt
from io import BytesIO

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

# Tablas fijas para uso interno (solo valores, no se muestran)
tabla_tipo_impacto = pd.DataFrame({
    "Código": ["H", "A", "E", "O", "I", "T", "R", "S", "C"],
    "Tipo de Impacto": [
        "Humano", "Ambiental", "Económico", "Operacional",
        "Infraestructura", "Tecnológico", "Reputacional",
        "Social", "Comercial"
    ],
    "Ponderación": [100, 85, 80, 75, 65, 60, 50, 45, 40],
    "Justificación": [
        "Afecta vida, salud o integridad. ISO 45001.",
        "Daños ecológicos graves. ISO 14001.",
        "Pérdidas financieras. COSO ERM.",
        "Interrumpe procesos críticos. ISO 22301.",
        "Daño a instalaciones o activos.",
        "Fallas o ciberataques. ISO 27005.",
        "Afecta imagen y confianza. COSO ERM.",
        "Impacta comunidades o responsabilidad social.",
        "Pérdida de clientes o mercado."
    ]
})

tabla_exposicion = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
    "Descripcion": [
        "Exposición muy rara",
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

# Clasificación criticidad
def clasificar_criticidad(valor):
    if valor <= 0.7:
        return "ACEPTABLE", "#008000"
    elif valor <= 3:
        return "TOLERABLE", "#FFD700"
    elif valor <= 7:
        return "INACEPTABLE", "#FF8C00"
    else:
        return "INADMISIBLE", "#FF0000"

# Calcular valores de riesgo
def calcular_criticidad(prob, expos, amenaza_delib, efectiv, val_impacto, pond_impacto):
    amenaza_inherente = prob * expos
    amenaza_residual = amenaza_inherente * (1 - efectiv)
    amenaza_residual_ajustada = amenaza_residual * amenaza_delib
    riesgo_residual = amenaza_residual_ajustada * val_impacto * (pond_impacto / 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

# Session state para riesgos acumulados
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

# Selector idioma
with st.sidebar.expander("Language / Idioma", expanded=True):
    idioma = st.selectbox("Selecciona idioma / Select language", ["es", "en"], index=0)

# Traducciones simplificadas para tablas fijas y variables
if idioma == "es":
    texto = textos["es"]
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto
    tabla_exposicion_mostrar = tabla_exposicion
    tabla_probabilidad_mostrar = tabla_probabilidad
    tabla_impacto_mostrar = tabla_impacto
else:
    texto = textos["en"]
    # Traduce tabla_tipo_impacto para mostrar con texto en inglés
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto.rename(columns={
        "Código": "Code",
        "Tipo de Impacto": "Impact Type",
        "Ponderación": "Weighting",
        "Justificación": "Justification"
    })
    tabla_tipo_impacto_mostrar["Tipo de Impacto"] = tabla_tipo_impacto_mostrar["Impact Type"]
    tabla_exposicion_mostrar = tabla_exposicion.rename(columns={
        "Nivel": "Level",
        "Descripcion": "Description"
    })
    tabla_probabilidad_mostrar = tabla_probabilidad.rename(columns={
        "Nivel": "Level",
        "Descripcion": "Description"
    })
    tabla_impacto_mostrar = tabla_impacto.rename(columns={
        "Descripcion": "Description"
    })

# Layout: formulario a la izquierda (60%), gráficos a la derecha (40%)
col_form, col_graficos = st.columns([3, 2])

with col_form:
    st.header(texto["resultados"])

    nombre_riesgo = st.text_input(texto["nombre_riesgo"])
    descripcion = st.text_area(texto["descripcion_riesgo"])

    # Tipo Impacto con justificación y ponderación interna
    opciones_impacto = [f"{row['Código']} - {row['Tipo de Impacto']}" for _, row in tabla_tipo_impacto.iterrows()]
    seleccion_impacto = st.selectbox(texto["tipo_impacto"], opciones_impacto)
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    justificacion = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Justificación"].values[0]
    ponderacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Ponderación"].values[0]
    st.markdown(f"**{texto['justificacion']}:** {justificacion}")

    # Listas desplegables con texto descriptivo
    exposicion = st.selectbox(
        texto["factor_exposicion"],
        options=tabla_exposicion_mostrar["Factor"],
        format_func=lambda x: f"{x} - {tabla_exposicion_mostrar.loc[tabla_exposicion_mostrar['Factor'] == x, 'Nivel' if idioma=='es' else 'Level'].values[0]}"
    )

    probabilidad = st.selectbox(
        texto["factor_probabilidad"],
        options=tabla_probabilidad_mostrar["Factor"],
        format_func=lambda x: f"{x} - {tabla_probabilidad_mostrar.loc[tabla_probabilidad_mostrar['Factor'] == x, 'Nivel' if idioma=='es' else 'Level'].values[0]}"
    )

    amenaza_deliberada = st.selectbox(
        texto["amenaza_deliberada"],
        options=[1, 2, 3],
        format_func=lambda x: texto["amenaza_deliberada_opciones"][x],
        index=0
    )

    efectividad = st.slider(texto["efectividad_control"], 0, 100, 50)

    impacto = st.selectbox(
        texto["impacto"],
        options=tabla_impacto_mostrar["Nivel"],
        format_func=lambda x: f"{x} - {tabla_impacto_mostrar.loc[tabla_impacto_mostrar['Nivel'] == x, 'Descripcion' if idioma=='es' else 'Description'].values[0]}"
    )

    # Calcular criticidad
    efectividad_norm = efectividad / 100
    valor_impacto = tabla_impacto_mostrar.loc[tabla_impacto_mostrar["Nivel"] == impacto, "Valor"].values[0]

    amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual = calcular_criticidad(
        probabilidad, exposicion, amenaza_deliberada, efectividad_norm, valor_impacto, ponderacion_impacto
    )

    clasificacion, color_criticidad = clasificar_criticidad(riesgo_residual)

    st.markdown(f"### {texto['resultados']}:")
    st.write(f"- {texto['amenaza_inherente']}: {amenaza_inherente:.4f}")
    st.write(f"- {texto['amenaza_residual']}: {amenaza_residual:.4f}")
    st.write(f"- {texto['amenaza_residual_ajustada']}: {amenaza_residual_ajustada:.4f}")
    st.write(f"- {texto['riesgo_residual']}: {riesgo_residual:.4f}")
    st.markdown(f"- {texto['clasificacion']}: <span style='color:{color_criticidad}; font-weight:bold'>{clasificacion}</span>", unsafe_allow_html=True)

    # Botón verde para agregar riesgo
    if st.button(texto["agregar_riesgo"], key="btn_agregar", help="Agregar riesgo a la matriz acumulativa"):
        if nombre_riesgo.strip() == "":
            st.warning("Debe ingresar un nombre para el riesgo.")
        else:
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
                "Color Criticidad": color_criticidad
            }
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
            st.success(texto["exito_agregar"])

with col_graficos:
    st.header(texto["mapa_calor_titulo"])

    if not st.session_state.riesgos.empty:
        # Valor mapa para heatmap (Amenaza Residual * Valor Impacto)
        st.session_state.riesgos["Valor Mapa"] = (
            st.session_state.riesgos["Amenaza Residual"] *
            st.session_state.riesgos["Impacto"].map(
                lambda x: tabla_impacto_mostrar.loc[tabla_impacto_mostrar["Nivel"] == x, "Valor"].values[0]
            )
        )

        # Mapa de calor interactivo con Plotly
        matriz_calor = st.session_state.riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Probabilidad",
            values="Valor Mapa",
            aggfunc=np.mean
        ).fillna(0).sort_index()

        heatmap_data = matriz_calor.reset_index().melt(id_vars="Tipo Impacto", var_name="Probabilidad", value_name="Valor")

        fig_heatmap = px.density_heatmap(
            heatmap_data,
            x="Probabilidad",
            y="Tipo Impacto",
            z="Valor",
            color_continuous_scale=["green", "yellow", "orange", "red"],
            title=texto["mapa_calor_titulo"],
            labels={"Probabilidad": texto["factor_probabilidad_titulo"], "Tipo Impacto": texto["tipo_impacto_titulo"], "Valor": "Valor Mapa"}
        )
        fig_heatmap.update_layout(height=450, margin=dict(l=40, r=40, t=50, b=40))
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Gráfico Pareto interactivo con Altair
        df_pareto = st.session_state.riesgos.copy()
        df_pareto = df_pareto.sort_values(by="Riesgo Residual", ascending=False)
        df_pareto["% Riesgo"] = 100 * df_pareto["Riesgo Residual"] / df_pareto["Riesgo Residual"].sum()
        df_pareto["% Acumulado"] = df_pareto["% Riesgo"].cumsum()

        base = alt.Chart(df_pareto).encode(x=alt.X('Nombre Riesgo:N', sort='-y', title=''))

        bar = base.mark_bar(color='skyblue').encode(y=alt.Y('% Riesgo:Q', title="% Riesgo Individual"))
        line = base.mark_line(color='red').encode(y=alt.Y('% Acumulado:Q', title="% Riesgo Acumulado", axis=alt.Axis(grid=False)))
        points = base.mark_point(color='red').encode(y='% Acumulado:Q')

        pareto_chart = alt.layer(bar, line, points).resolve_scale(
            y='independent'
        ).properties(
            width=600,
            height=400,
            title='Gráfico de Pareto de Riesgos' if idioma == "es" else 'Risk Pareto Chart'
        )

        st.altair_chart(pareto_chart, use_container_width=True)

    else:
        st.info(texto["info_agrega_riesgos"])

st.markdown("---")

# Matriz acumulativa abajo (full width)
st.header(texto["matriz_acumulativa_titulo"])

if not st.session_state.riesgos.empty:
    # Mostrar matriz acumulativa en tabla
    df_export = st.session_state.riesgos.copy()
    st.dataframe(df_export.style.apply(
        lambda x: ['background-color: ' + x['Color Criticidad'] if col == "Riesgo Residual" else '' for col in df_export.columns],
        axis=1
    ))

    # Función para exportar a Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Matriz Riesgos')
            writer.save()
        processed_data = output.getvalue()
        return processed_data

    excel_data = to_excel(df_export)

    st.download_button(
        label=texto["descargar_excel"],
        data=excel_data,
        file_name='matriz_riesgos.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        key="download-excel"
    )
else:
    st.info(texto["info_agrega_riesgos_matriz"])

# Estilos CSS para botones verdes y textos (puedes ampliar)
st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #4CAF50;
    color: white;
    font-weight: bold;
    border-radius: 5px;
    padding: 8px 18px;
}
div.stButton > button:first-child:hover {
    background-color: #45a049;
}
</style>
""", unsafe_allow_html=True)
