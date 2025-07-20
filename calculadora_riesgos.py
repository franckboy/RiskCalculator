import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

st.set_page_config(layout="wide")

# --- CSS personalizado ---
st.markdown("""
<style>
    /* Botones verdes visibles */
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
    /* Selectbox ancho y legible */
    div.stSelectbox > div[data-baseweb="select"] {
        width: 100% !important;
        font-size: 16px !important;
    }
    /* Textarea tamaño */
    textarea {
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Tablas de datos ---

# Tipo de impacto (español)
tabla_tipo_impacto = pd.DataFrame({
    "Código": ["1", "2", "3", "4", "5"],
    "Tipo de Impacto": ["Daño a la infraestructura crítica", "Pérdida de datos sensibles", "Interrupción operativa", "Daño reputacional", "Impacto financiero"],
    "Justificación": [
        "Daño que afecta elementos esenciales para operaciones.",
        "Pérdida o exposición de información confidencial.",
        "Suspensión parcial o total de actividades.",
        "Perjuicio en la imagen pública o confianza.",
        "Consecuencias económicas directas o indirectas."
    ],
    "Ponderación": [30, 25, 20, 15, 10]
})

# Exposición (español)
tabla_exposicion = pd.DataFrame({
    "Factor": [0.05, 0.2, 0.5, 0.75, 0.95],
    "Nivel": ["Muy baja", "Baja", "Media", "Alta", "Muy alta"]
})

# Probabilidad (español)
tabla_probabilidad = pd.DataFrame({
    "Factor": [0.01, 0.1, 0.3, 0.6, 0.85],
    "Nivel": ["Muy rara vez", "Rara vez", "Ocasionalmente", "Frecuentemente", "Muy frecuentemente"]
})

# Impacto (español)
tabla_impacto = pd.DataFrame({
    "Nivel": ["Muy bajo", "Bajo", "Medio", "Alto", "Muy alto"],
    "Valor": [1, 2, 4, 7, 10],
    "Descripcion": ["Impacto mínimo", "Impacto leve", "Impacto moderado", "Impacto serio", "Impacto catastrófico"]
})

# Textos español e inglés
textos = {
    "es": {
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion_riesgo": "Descripción del riesgo",
        "tipo_impacto": "Tipo de impacto",
        "justificacion": "Justificación",
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
        "info_agrega_riesgos": "Agrega riesgos para visualizar los gráficos.",
        "matriz_acumulativa_titulo": "Matriz Acumulativa de Riesgos",
        "descargar_excel": "Descargar matriz en Excel",
        "info_agrega_riesgos_matriz": "Agrega riesgos para mostrar la matriz acumulativa."
    },
    "en": {
        "nombre_riesgo": "Risk Name",
        "descripcion_riesgo": "Risk Description",
        "tipo_impacto": "Impact Type",
        "justificacion": "Justification",
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
        "info_agrega_riesgos": "Add risks to visualize charts.",
        "matriz_acumulativa_titulo": "Accumulated Risk Matrix",
        "descargar_excel": "Download matrix as Excel",
        "info_agrega_riesgos_matriz": "Add risks to show the accumulated matrix."
    }
}

# Funciones para clasificar criticidad (igual en ambos idiomas)
def clasificar_criticidad(valor):
    if valor <= 0.7:
        return "ACEPTABLE", "#008000"
    elif valor <= 3:
        return "TOLERABLE", "#FFD700"
    elif valor <= 7:
        return "INACEPTABLE", "#FF8C00"
    else:
        return "INADMISIBLE", "#FF0000"

def clasificar_criticidad_en(valor):
    if valor <= 0.7:
        return "ACCEPTABLE", "#008000"
    elif valor <= 3:
        return "TOLERABLE", "#FFD700"
    elif valor <= 7:
        return "UNACCEPTABLE", "#FF8C00"
    else:
        return "INTOLERABLE", "#FF0000"

# Función principal de cálculo
def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto):
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

# Guardar riesgos en sesión
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

# Selector idioma
idioma = st.sidebar.selectbox("Selecciona idioma / Select language", options=["es", "en"], index=0)

if idioma == "es":
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto
    tabla_exposicion_mostrar = tabla_exposicion
    tabla_probabilidad_mostrar = tabla_probabilidad
    tabla_impacto_mostrar = tabla_impacto
    clasificar_criticidad_usar = clasificar_criticidad
    textos_usar = textos["es"]
else:
    tabla_tipo_impacto_mostrar = tabla_tipo_impacto
    tabla_exposicion_mostrar = tabla_exposicion
    tabla_probabilidad_mostrar = tabla_probabilidad
    tabla_impacto_mostrar = tabla_impacto
    clasificar_criticidad_usar = clasificar_criticidad_en
    textos_usar = textos["en"]

# Layout: formularios izquierda (60%), gráficos derecha (40%)
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
    justificacion_impacto = tabla_tipo_impacto_mostrar.loc[tabla_tipo_impacto_mostrar["Código"] == codigo_impacto, "Justificación"].values[0]
    ponderacion_impacto = tabla_tipo_impacto_mostrar.loc[tabla_tipo_impacto_mostrar["Código"] == codigo_impacto, "Ponderación"].values[0]
    st.markdown(f"**{textos_usar['justificacion']}:** {justificacion_impacto}")

    exposicion = st.selectbox(
        textos_usar["factor_exposicion"],
        options=tabla_exposicion_mostrar["Factor"],
        format_func=lambda x: f"{x} - {tabla_exposicion_mostrar.loc[tabla_exposicion_mostrar['Factor']==x, 'Nivel'].values[0]}"
    )
    probabilidad = st.selectbox(
        textos_usar["factor_probabilidad"],
        options=tabla_probabilidad_mostrar["Factor"],
        format_func=lambda x: f"{x} - {tabla_probabilidad_mostrar.loc[tabla_probabilidad_mostrar['Factor']==x, 'Nivel'].values[0]}"
    )
    amenaza_deliberada = st.selectbox(
        textos_usar["amenaza_deliberada"],
        options=[1, 2, 3],
        format_func=lambda x: textos_usar["amenaza_deliberada_opciones"][x],
        index=0
    )
    efectividad = st.slider(textos_usar["efectividad_control"], 0, 100, 50)

    impacto = st.selectbox(
        textos_usar["impacto"],
        options=tabla_impacto_mostrar["Nivel"],
        format_func=lambda x: f"{x} - {tabla_impacto_mostrar.loc[tabla_impacto_mostrar['Nivel']==x, 'Descripcion'].values[0]}"
    )

    efectividad_norm = efectividad / 100
    valor_impacto = tabla_impacto_mostrar.loc[tabla_impacto_mostrar["Nivel"] == impacto, "Valor"].values[0]

    amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual = calcular_criticidad(
        probabilidad, exposicion, amenaza_deliberada, efectividad_norm, valor_impacto, ponderacion_impacto
    )

    clasificacion, color = clasificar_criticidad_usar(riesgo_residual)

    st.markdown(f"### {textos_usar['resultados']}:")
    st.write(f"- {textos_usar['amenaza_inherente']}: {amenaza_inherente:.4f}")
    st.write(f"- {textos_usar['amenaza_residual']}: {amenaza_residual:.4f}")
    st.write(f"- {textos_usar['amenaza_residual_ajustada']}: {amenaza_residual_ajustada:.4f}")
    st.write(f"- {textos_usar['riesgo_residual']}: {riesgo_residual:.4f}")
    st.write(f"- {textos_usar['clasificacion']}: **{clasificacion}**")

    btn_agregar = st.button(textos_usar["agregar_riesgo"])

    if btn_agregar:
        if nombre_riesgo.strip() == "":
            st.error("Debe ingresar un nombre para el riesgo.")
        else:
            nuevo_riesgo = {
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
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
            st.success(textos_usar["exito_agregar"])

with col_graf:
    st.header(textos_usar["mapa_calor_titulo"])

    if not st.session_state.riesgos.empty:
        df = st.session_state.riesgos.copy()

        # Mapa de calor Plotly
        heatmap_df = df.groupby(["Tipo Impacto", "Probabilidad"]).agg(
            {"Amenaza Residual Ajustada": "mean"}).reset_index()

        heatmap_df["Tipo Impacto"] = pd.Categorical(
            heatmap_df["Tipo Impacto"], categories=tabla_tipo_impacto_mostrar["Código"], ordered=True)

        fig_heatmap = px.density_heatmap(
            heatmap_df,
            x="Probabilidad",
            y="Tipo Impacto",
            z="Amenaza Residual Ajustada",
            color_continuous_scale="RdYlGn_r",
            labels={
                "Probabilidad": textos_usar["factor_probabilidad"],
                "Tipo Impacto": textos_usar["tipo_impacto"],
                "Amenaza Residual Ajustada": textos_usar["amenaza_residual_ajustada"]
            },
            title=textos_usar["mapa_calor_titulo"],
            nbinsx=5,
            nbinsy=len(tabla_tipo_impacto_mostrar)
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Gráfico Pareto
        st.subheader("Pareto - Riesgos Residuales")

        pareto_df = df[["Nombre Riesgo", "Riesgo Residual"]].sort_values("Riesgo Residual", ascending=False).head(10)
        pareto_df["Acumulado"] = pareto_df["Riesgo Residual"].cumsum()
        pareto_df["Porcentaje Acumulado"] = 100 * pareto_df["Acumulado"] / pareto_df["Riesgo Residual"].sum()

        fig_pareto = px.bar(
            pareto_df,
            x="Nombre Riesgo",
            y="Riesgo Residual",
            labels={"Riesgo Residual": "Residual Risk", "Nombre Riesgo": "Risk Name"},
            title="Top 10 Riesgos Residuales" if idioma == "es" else "Top 10 Residual Risks",
            color_discrete_sequence=["green"]
        )
        fig_pareto.add_scatter(
            x=pareto_df["Nombre Riesgo"],
            y=pareto_df["Porcentaje Acumulado"],
            mode="lines+markers",
            name="Acumulado (%)",
            yaxis="y2",
            line=dict(color="orange")
        )
        fig_pareto.update_layout(
            yaxis2=dict(
                overlaying="y",
                side="right",
                range=[0, 110],
                title="Acumulado (%)"
            ),
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

    else:
        st.info(textos_usar["info_agrega_riesgos"])

st.markdown("---")
st.header(textos_usar["matriz_acumulativa_titulo"])

if not st.session_state.riesgos.empty:
    df_export = st.session_state.riesgos.copy()

    def color_riesgo(row):
        return ['background-color: ' + row['Color Criticidad'] if col == "Riesgo Residual" else '' for col in row.index]

    st.dataframe(df_export.style.apply(color_riesgo, axis=1))

    # Botón descarga Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, sheet_name='Matriz de Riesgos', index=False)
    st.download_button(
        label=textos_usar["descargar_excel"],
        data=output.getvalue(),
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info(textos_usar["info_agrega_riesgos_matriz"])
