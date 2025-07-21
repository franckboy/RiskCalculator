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

# --- Definición de tablas internas (no visibles) ---

# Tabla tipo impacto (códigos y ponderaciones)
tabla_tipo_impacto = pd.DataFrame({
    "Código": ["H", "O", "E", "I", "T", "R", "A", "C", "S"],
    "Nombre": ["Humano", "Operacional", "Económico", "Infraestructura", "Tecnológico", "Reputacional", "Ambiental", "Comercial", "Social"],
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

# Tabla factor exposición
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

# Tabla factor probabilidad
tabla_probabilidad = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
    "Definición": [
        "En condiciones excepcionales",
        "Ha sucedido alguna vez",
        "Podría ocurrir ocasionalmente",
        "Probable en ocasiones",
        "Ocurre con frecuencia / inminente"
    ]
})

# Tabla impacto/severidad
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

# Tabla efectividad controles
tabla_efectividad = pd.DataFrame({
    "Rango": ["0%", "1-20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
    "Factor": [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0],
    "Mitigacion": ["Inefectiva", "Limitada", "Baja", "Intermedia", "Alta", "Muy alta", "Total"],
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

# Clasificación criticidad (Índice y Aceptabilidad)
def clasificar_indice_criticidad(valor):
    if valor <= 2:
        return "ACEPTABLE", "#008000"  # verde
    elif valor <= 4:
        return "TOLERABLE", "#FFD700"  # amarillo
    elif valor <= 15:
        return "INACEPTABLE", "#FF8C00"  # naranja
    else:
        return "INADMISIBLE", "#FF0000"  # rojo

def clasificar_aceptabilidad(valor):
    if valor <= 0.7:
        return "ACEPTABLE", "#008000"
    elif valor <= 3.0:
        return "TOLERABLE", "#FFD700"
    elif valor <= 7.0:
        return "INACEPTABLE", "#FF8C00"
    else:
        return "INADMISIBLE", "#FF0000"

# --- Función de cálculo del riesgo ---
def calcular_riesgo(probabilidad, exposicion, efectividad_control, impacto_valor, ponderacion_impacto):
    # Amenaza inherente: probabilidad x exposición
    amenaza_inherente = probabilidad * exposicion
    # Ajuste por efectividad control (factor entre 0 y 1)
    amenaza_residual = amenaza_inherente * (1 - efectividad_control)
    # Riesgo residual considerando impacto y ponderación
    riesgo_residual = amenaza_residual * impacto_valor * (ponderacion_impacto / 100)
    return amenaza_inherente, amenaza_residual, riesgo_residual

# --- Inicializar estado ---
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad",
        "Efectividad Control", "Impacto", "Amenaza Inherente", "Amenaza Residual",
        "Riesgo Residual", "Clasificación", "Color"
    ])

# --- Selector idioma (por simplicidad solo español aquí, pero se puede extender) ---
idioma = "es"

# --- Layout ---
col_form, col_graf = st.columns([3,2])

with col_form:
    st.header("Calculadora de Riesgos")

    nombre_riesgo = st.text_input("Nombre del riesgo")
    descripcion = st.text_area("Descripción del riesgo")

    # Tipo impacto (mostrar nombre + código + explicación breve)
    opciones_impacto = [
        f"{row['Código']} - {row['Nombre']} ({row['Explicación']})"
        for _, row in tabla_tipo_impacto.iterrows()
    ]
    seleccion_impacto = st.selectbox("Tipo de Impacto", opciones_impacto)
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    ponderacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Ponderación"].values[0]

    # Factor exposición con descripción
    opciones_exposicion = [
        f"{row['Factor']:.2f} - {row['Nivel']} ({row['Definición']})"
        for _, row in tabla_exposicion.iterrows()
    ]
    seleccion_exposicion = st.selectbox("Factor de Exposición", opciones_exposicion)
    exposicion = float(seleccion_exposicion.split(" - ")[0])

    # Factor probabilidad con descripción
    opciones_probabilidad = [
        f"{row['Factor']:.2f} - {row['Nivel']} ({row['Definición']})"
        for _, row in tabla_probabilidad.iterrows()
    ]
    seleccion_probabilidad = st.selectbox("Factor de Probabilidad", opciones_probabilidad)
    probabilidad = float(seleccion_probabilidad.split(" - ")[0])

    # Efectividad control con descripción (usar rango para mostrar pero factor para calcular)
    opciones_efectividad = [
        f"{row['Rango']} - {row['Mitigacion']} ({row['Descripción']})"
        for _, row in tabla_efectividad.iterrows()
    ]
    seleccion_efectividad = st.selectbox("Efectividad de Controles", opciones_efectividad)
    # Extraer factor
    idx_efectividad = opciones_efectividad.index(seleccion_efectividad)
    efectividad_control = tabla_efectividad.iloc[idx_efectividad]["Factor"]

    # Impacto con descripción
    opciones_impacto_valor = [
        f"{row['Valor']} - {row['Clasificación']} ({row['Definición']})"
        for _, row in tabla_impacto.iterrows()
    ]
    seleccion_impacto_valor = st.selectbox("Impacto", opciones_impacto_valor)
    impacto_valor = int(seleccion_impacto_valor.split(" - ")[0])

    # Calcular riesgos
    amenaza_inherente, amenaza_residual, riesgo_residual = calcular_riesgo(
        probabilidad, exposicion, efectividad_control, impacto_valor, ponderacion_impacto
    )

    # Clasificar criticidad índice (usar riesgo residual)
    clasificacion, color = clasificar_indice_criticidad(riesgo_residual)

    st.markdown("### Resultados:")
    st.write(f"Amenaza Inherente: {amenaza_inherente:.4f}")
    st.write(f"Amenaza Residual: {amenaza_residual:.4f}")
    st.write(f"Riesgo Residual: {riesgo_residual:.4f}")
    st.write(f"Clasificación: **{clasificacion}**")

    # Botón para agregar riesgo
    if st.button("Agregar riesgo"):
        if nombre_riesgo.strip() == "":
            st.error("Debe ingresar un nombre para el riesgo.")
        else:
            nuevo_riesgo = {
                "Nombre Riesgo": nombre_riesgo,
                "Descripción": descripcion,
                "Tipo Impacto": codigo_impacto,
                "Exposición": exposicion,
                "Probabilidad": probabilidad,
                "Efectividad Control": efectividad_control,
                "Impacto": impacto_valor,
                "Amenaza Inherente": amenaza_inherente,
                "Amenaza Residual": amenaza_residual,
                "Riesgo Residual": riesgo_residual,
                "Clasificación": clasificacion,
                "Color": color
            }
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
            st.success("Riesgo agregado exitosamente")

with col_graf:
    st.header("Visualizaciones")

    if not st.session_state.riesgos.empty:
        df = st.session_state.riesgos.copy()

        # Mapa de calor con Plotly
        heatmap_df = df.groupby(["Tipo Impacto", "Probabilidad"]).agg({"Riesgo Residual": "mean"}).reset_index()

        # Ordenar categorías de tipo impacto
        heatmap_df["Tipo Impacto"] = pd.Categorical(
            heatmap_df["Tipo Impacto"], categories=tabla_tipo_impacto["Código"], ordered=True
        )

        fig_heatmap = px.density_heatmap(
            heatmap_df,
            x="Probabilidad",
            y="Tipo Impacto",
            z="Riesgo Residual",
            color_continuous_scale="RdYlGn_r",
            labels={
                "Probabilidad": "Factor de Probabilidad",
                "Tipo Impacto": "Tipo de Impacto",
                "Riesgo Residual": "Riesgo Residual"
            },
            title="Mapa de Calor de Riesgos",
            nbinsx=5,
            nbinsy=len(tabla_tipo_impacto)
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

        # Gráfico Pareto de riesgos
        st.subheader("Pareto - Top Riesgos Residuales")

        pareto_df = df[["Nombre Riesgo", "Riesgo Residual"]].sort_values("Riesgo Residual", ascending=False).head(10)
        pareto_df["Acumulado"] = pareto_df["Riesgo Residual"].cumsum()
        pareto_df["Porcentaje Acumulado"] = 100 * pareto_df["Acumulado"] / pareto_df["Riesgo Residual"].sum()

        fig_pareto = px.bar(
            pareto_df,
            x="Nombre Riesgo",
            y="Riesgo Residual",
            labels={"Riesgo Residual": "Riesgo Residual", "Nombre Riesgo": "Nombre Riesgo"},
            color_discrete_sequence=["green"],
            title="Top 10 Riesgos Residuales"
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
        st.info("Agrega riesgos para visualizar los gráficos.")

st.markdown("---")
st.header("Matriz Acumulativa de Riesgos")

if not st.session_state.riesgos.empty:
    df_export = st.session_state.riesgos.copy()

    def color_filas(row):
        return ['background-color: ' + row['Color'] if col == "Riesgo Residual" else '' for col in row.index]

    st.dataframe(df_export.style.apply(color_filas, axis=1))

    # Botón descarga Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_export.to_excel(writer, sheet_name='Matriz de Riesgos', index=False)
    st.download_button(
        label="Descargar matriz en Excel",
        data=output.getvalue(),
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Agrega riesgos para mostrar la matriz acumulativa.")
