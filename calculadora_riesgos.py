import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO

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

# === TABLAS DE DATOS ===

tabla_tipo_impacto = pd.DataFrame({
    "Código": ["H", "O", "E", "I", "T", "R", "A", "C", "S"],
    "Tipo de Impacto": [
        "Humano (H)", "Operacional (O)", "Económico (E)", "Infraestructura (I)",
        "Tecnológico (T)", "Reputacional (R)", "Ambiental (A)", "Comercial (C)", "Social (S)"
    ],
    "Ponderación": [25, 20, 15, 12, 10, 8, 5, 3, 2],
    "Explicación": [
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

tabla_exposicion = pd.DataFrame({
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

tabla_probabilidad = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
    "Descripción": [
        "En condiciones excepcionales",
        "Ha sucedido alguna vez",
        "Podría ocurrir ocasionalmente",
        "Probable en ocasiones",
        "Ocurre con frecuencia / inminente"
    ]
})

tabla_efectividad = pd.DataFrame({
    "Rango": ["0%", "1-20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
    "Factor": [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.1],
    "Mitigación": ["Inefectiva", "Limitada", "Baja", "Intermedia", "Alta", "Muy alta", "Total"],
    "Descripción": [
        "No reduce el riesgo",
        "Reduce solo en condiciones ideales",
        "Mitiga riesgos menores.",
        "Control estándar con limitaciones.",
        "Reduce significativamente el riesgo",
        "Control robusto y bien implementado.",
        "Elimina casi todo el riesgo"
    ]
})

tabla_impacto = pd.DataFrame({
    "Nivel": [1, 2, 3, 4, 5],
    "Valor": [5, 10, 30, 60, 85],
    "Clasificación": ["Insignificante", "Leve", "Moderado", "Grave", "Crítico"],
    "Definición": [
        "No afecta significativamente",
        "Afectación menor",
        "Afectación parcial y temporal",
        "Afectación significativa",
        "Impacto serio o pérdida total"
    ]
})

# Índices de criticidad para clasificar riesgos
def clasificar_criticidad(valor, idioma):
    if idioma == "es":
        if valor <= 0.7:
            return "ACEPTABLE", "#008000"
        elif valor <= 3:
            return "TOLERABLE", "#FFD700"
        elif valor <= 7:
            return "INACEPTABLE", "#FF8C00"
        else:
            return "INADMISIBLE", "#FF0000"
    else:  # English
        if valor <= 0.7:
            return "ACCEPTABLE", "#008000"
        elif valor <= 3:
            return "TOLERABLE", "#FFD700"
        elif valor <= 7:
            return "UNACCEPTABLE", "#FF8C00"
        else:
            return "INTOLERABLE", "#FF0000"

# Textos para multilenguaje
textos = {
    "es": {
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion_riesgo": "Descripción del riesgo",
        "tipo_impacto": "Tipo de impacto",
        "justificacion": "Explicación",
        "factor_exposicion": "Factor de exposición",
        "factor_probabilidad": "Factor de probabilidad",
        "amenaza_deliberada": "Amenaza deliberada",
        "amenaza_deliberada_opciones": {1: "No", 2: "Sí baja", 3: "Sí alta"},
        "efectividad_control": "Efectividad del control (%)",
        "impacto": "Impacto / Severidad",
        "agregar_riesgo": "Agregar riesgo",
        "exito_agregar": "Riesgo agregado exitosamente",
        "resultados": "Resultados",
        "amenaza_inherente": "Amenaza Inherente",
        "amenaza_residual": "Amenaza Residual",
        "amenaza_residual_ajustada": "Amenaza Residual Ajustada",
        "riesgo_residual": "Riesgo Residual",
        "clasificacion": "Clasificación",
        "mapa_calor_titulo": "Mapa de Calor de Riesgos",
        "pareto_titulo": "Pareto de Riesgos Residuales",
        "info_agrega_riesgos": "Agrega riesgos para visualizar los gráficos.",
        "matriz_acumulativa_titulo": "Matriz Acumulativa de Riesgos",
        "descargar_excel": "Descargar matriz en Excel",
        "info_agrega_riesgos_matriz": "Agrega riesgos para mostrar la matriz acumulativa."
    },
    "en": {
        "nombre_riesgo": "Risk Name",
        "descripcion_riesgo": "Risk Description",
        "tipo_impacto": "Impact Type",
        "justificacion": "Explanation",
        "factor_exposicion": "Exposure Factor",
        "factor_probabilidad": "Probability Factor",
        "amenaza_deliberada": "Deliberate Threat",
        "amenaza_deliberada_opciones": {1: "No", 2: "Low", 3: "High"},
        "efectividad_control": "Control Effectiveness (%)",
        "impacto": "Impact / Severity",
        "agregar_riesgo": "Add Risk",
        "exito_agregar": "Risk added successfully",
        "resultados": "Results",
        "amenaza_inherente": "Inherent Threat",
        "amenaza_residual": "Residual Threat",
        "amenaza_residual_ajustada": "Adjusted Residual Threat",
        "riesgo_residual": "Residual Risk",
        "clasificacion": "Classification",
        "mapa_calor_titulo": "Risk Heatmap",
        "pareto_titulo": "Residual Risks Pareto",
        "info_agrega_riesgos": "Add risks to visualize charts.",
        "matriz_acumulativa_titulo": "Accumulated Risk Matrix",
        "descargar_excel": "Download matrix as Excel",
        "info_agrega_riesgos_matriz": "Add risks to show the accumulated matrix."
    }
}

# --- Función para cálculo principal ---
def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto):
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

# --- Inicializar riesgos en sesión ---
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

# --- Selector idioma (checkbox en sidebar) ---
st.sidebar.title("Configuración / Settings")
idioma = "es" if st.sidebar.checkbox("Español / Spanish", value=True) else "en"
txt = textos[idioma]

# --- Layout columnas ---
col_form, col_graf = st.columns([3, 2])

with col_form:
    st.title("Calculadora de Riesgos" if idioma == "es" else "Risk Calculator")
    st.subheader(txt["resultados"])

    # Entradas formulario
    nombre_riesgo = st.text_input(txt["nombre_riesgo"])
    descripcion = st.text_area(txt["descripcion_riesgo"])

    opciones_impacto = [
        f"{row['Código']} - {row['Tipo de Impacto']}" for _, row in tabla_tipo_impacto.iterrows()
    ]
    seleccion_impacto = st.selectbox(txt["tipo_impacto"], opciones_impacto)
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    justificacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Explicación"].values[0]
    ponderacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Ponderación"].values[0]
    st.markdown(f"**{txt['justificacion']}:** {justificacion_impacto}")

    exposicion = st.selectbox(
        txt["factor_exposicion"],
        options=tabla_exposicion["Factor"],
        format_func=lambda x: f"{x:.2f} - {tabla_exposicion.loc[tabla_exposicion['Factor']==x, 'Nivel'].values[0]} - {tabla_exposicion.loc[tabla_exposicion['Factor']==x, 'Definición'].values[0]}"
    )

    probabilidad = st.selectbox(
        txt["factor_probabilidad"],
        options=tabla_probabilidad["Factor"],
        format_func=lambda x: f"{x:.2f} - {tabla_probabilidad.loc[tabla_probabilidad['Factor']==x, 'Nivel'].values[0]} - {tabla_probabilidad.loc[tabla_probabilidad['Factor']==x, 'Descripción'].values[0]}"
    )

    amenaza_deliberada = st.selectbox(
        txt["amenaza_deliberada"],
        options=[1, 2, 3],
        format_func=lambda x: txt["amenaza_deliberada_opciones"][x],
        index=0
    )

    efectividad_porcentaje = st.slider(txt["efectividad_control"], 0, 100, 50)
    efectividad = efectividad_porcentaje / 100

    impacto = st.selectbox(
        txt["impacto"],
        options=tabla_impacto["Nivel"],
        format_func=lambda x: f"{x} - {tabla_impacto.loc[tabla_impacto['Nivel']==x, 'Clasificación'].values[0]} - {tabla_impacto.loc[tabla_impacto['Nivel']==x, 'Definición'].values[0]}"
    )

    valor_impacto = tabla_impacto.loc[tabla_impacto["Nivel"] == impacto, "Valor"].values[0]

    # Cálculo
    amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual = calcular_criticidad(
        probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto
    )

    clasificacion, color = clasificar_criticidad(riesgo_residual, idioma)

    # Mostrar resultados
    st.markdown(f"### {txt['resultados']}:")
    st.write(f"- {txt['amenaza_inherente']}: {amenaza_inherente:.4f}")
    st.write(f"- {txt['amenaza_residual']}: {amenaza_residual:.4f}")
    st.write(f"- {txt['amenaza_residual_ajustada']}: {amenaza_residual_ajustada:.4f}")
    st.write(f"- {txt['riesgo_residual']}: {riesgo_residual:.4f}")
    st.write(f"- {txt['clasificacion']}: **{clasificacion}**")

    if st.button(txt["agregar_riesgo"]):
        if nombre_riesgo.strip() == "":
            st.error("Debe ingresar un nombre para el riesgo." if idioma=="es" else "You must enter a risk name.")
        else:
            nuevo_riesgo = {
                "Nombre Riesgo": nombre_riesgo,
                "Descripción": descripcion,
                "Tipo Impacto": codigo_impacto,
                "Exposición": exposicion,
                "Probabilidad": probabilidad,
                "Amenaza Deliberada": amenaza_deliberada,
                "Efectividad Control (%)": efectividad_porcentaje,
                "Impacto": impacto,
                "Amenaza Inherente": amenaza_inherente,
                "Amenaza Residual": amenaza_residual,
                "Amenaza Residual Ajustada": amenaza_residual_ajustada,
                "Riesgo Residual": riesgo_residual,
                "Clasificación Criticidad": clasificacion,
                "Color Criticidad": color
            }
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
            st.success(txt["exito_agregar"])

with col_graf:
    st.header(txt["mapa_calor_titulo"])

    if not st.session_state.riesgos.empty:
        df = st.session_state.riesgos.copy()

        # Categorías ordenadas para filas y columnas
        categorias_impacto = tabla_tipo_impacto["Código"].tolist()
        categorias_probabilidad = tabla_probabilidad["Factor"].round(2).tolist()

        # Redondear para coincidir
        df["Probabilidad_rounded"] = df["Probabilidad"].round(2)

        heatmap_data = (
            df.groupby(["Tipo Impacto", "Probabilidad_rounded"])
            .agg({"Riesgo Residual": "mean"})
            .reset_index()
            .pivot(index="Tipo Impacto", columns="Probabilidad_rounded", values="Riesgo Residual")
            .reindex(index=categorias_impacto, columns=categorias_probabilidad)
        )

        heatmap_data = heatmap_data.fillna(0)

        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x=txt["factor_probabilidad"], y=txt["tipo_impacto"], color=txt["riesgo_residual"]),
            x=[f"{p:.2f}" for p in heatmap_data.columns],
            y=[f"{c}" for c in heatmap_data.index],
            color_continuous_scale="RdYlGn_r",
            aspect="auto",
        )
        fig_heatmap.update_layout(
            title=txt["mapa_calor_titulo"],
            xaxis_title=txt["factor_probabilidad"],
            yaxis_title=txt["tipo_impacto"],
            margin=dict(l=60, r=10, t=50, b=50)
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.subheader(txt["pareto_titulo"])

        pareto_df = df[["Nombre Riesgo", "Riesgo Residual"]].sort_values("Riesgo Residual", ascending=False).head(10)
        pareto_df["Acumulado"] = pareto_df["Riesgo Residual"].cumsum()
        pareto_df["Porcentaje Acumulado"] = 100 * pareto_df["Acumulado"] / pareto_df["Riesgo Residual"].sum()

        fig_pareto = px.bar(
            pareto_df,
            x="Nombre Riesgo",
            y="Riesgo Residual",
            labels={"Riesgo Residual": txt["riesgo_residual"], "Nombre Riesgo": txt["nombre_riesgo"]},
            title=txt["pareto_titulo"],
            color_discrete_sequence=["green"]
        )

        fig_pareto.add_scatter(
            x=pareto_df["Nombre Riesgo"],
            y=pareto_df["Porcentaje Acumulado"],
            mode="lines+markers",
            name="Acumulado (%)",
            yaxis="y2",
            line=dict(color="orange", width=2),
        )

        fig_pareto.update_layout(
            yaxis2=dict(
                overlaying="y",
                side="right",
                range=[0, 110],
                title="Acumulado (%)",
                showgrid=False,
            ),
            xaxis_tickangle=-45,
            margin=dict(l=40, r=60, t=60, b=120),
            legend=dict(y=1.1, orientation="h")
        )

        st.plotly_chart(fig_pareto, use_container_width=True)

        # Matriz Acumulativa (tabla)
        st.subheader(txt["matriz_acumulativa_titulo"])
        matriz_acum = df.groupby("Tipo Impacto").agg({
            "Riesgo Residual": "sum"
        }).rename(columns={"Riesgo Residual": txt["riesgo_residual"]})
        st.dataframe(matriz_acum.style.background_gradient(cmap="RdYlGn_r"))

        # Descargar Excel
        def to_excel(df):
            output = BytesIO()
            writer = pd.ExcelWriter(output, engine="xlsxwriter")
            df.to_excel(writer, index=True, sheet_name="Matriz")
            writer.save()
            processed_data = output.getvalue()
            return processed_data

        excel_data = to_excel(matriz_acum)

        st.download_button(
            label=txt["descargar_excel"],
            data=excel_data,
            file_name="matriz_riesgos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info(txt["info_agrega_riesgos"])


