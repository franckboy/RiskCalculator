import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap

st.set_page_config(layout="wide", page_title="Calculadora de Riesgos")

# --- Traducciones ---
textos = {
    "es": {
        "factor_exposicion": "Factor de Exposición",
        "factor_probabilidad": "Factor de Probabilidad",
        "impacto": "Impacto",
        "tipo_impacto": "Tipo de Impacto",
        "justificacion": "Justificación",
        "amenaza_deliberada": "Amenaza Deliberada",
        "amenaza_deliberada_opciones": {1: "Baja", 2: "Intermedia", 3: "Alta"},
        "efectividad_control": "Efectividad del Control (%)",
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion_riesgo": "Descripción del riesgo",
        "agregar_riesgo": "Agregar riesgo a la matriz",
        "exito_agregar": "Riesgo agregado a la matriz.",
        "mapa_calor_titulo": "Mapa de Calor: Probabilidad (Amenaza Residual) vs Impacto",
        "pareto_titulo": "Gráfico de Pareto de Riesgos",
        "matriz_acumulativa_titulo": "Matriz Acumulativa de Riesgos",
        "descargar_excel": "Descargar matriz en Excel",
        "clasificacion": "Clasificación",
        "riesgo_residual": "Riesgo Residual",
        "info_agrega_riesgos": "Agrega riesgos para mostrar gráficos y matriz.",
    },
    "en": {
        "factor_exposicion": "Exposure Factor",
        "factor_probabilidad": "Probability Factor",
        "impacto": "Impact",
        "tipo_impacto": "Impact Type",
        "justificacion": "Justification",
        "amenaza_deliberada": "Deliberate Threat",
        "amenaza_deliberada_opciones": {1: "Low", 2: "Intermediate", 3: "High"},
        "efectividad_control": "Control Effectiveness (%)",
        "nombre_riesgo": "Risk Name",
        "descripcion_riesgo": "Risk Description",
        "agregar_riesgo": "Add risk to matrix",
        "exito_agregar": "Risk added to matrix.",
        "mapa_calor_titulo": "Heatmap: Probability (Residual Threat) vs Impact",
        "pareto_titulo": "Risk Pareto Chart",
        "matriz_acumulativa_titulo": "Cumulative Risk Matrix",
        "descargar_excel": "Download matrix as Excel",
        "clasificacion": "Classification",
        "riesgo_residual": "Residual Risk",
        "info_agrega_riesgos": "Add risks to show charts and matrix.",
    }
}

# --- Tablas fijas para cálculos (NO mostrar en interfaz) ---
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
        "Daños ecológicos y sanciones. ISO 14001.",
        "Pérdidas financieras. COSO ERM.",
        "Interrupción procesos clave. ISO 22301.",
        "Daños físicos a activos.",
        "Fallas sistemas o ciberataques. ISO 27005.",
        "Impacto en imagen pública.",
        "Impacto social y laboral. ISO 26000.",
        "Pérdida de mercado o contratos."
    ]
})

tabla_exposicion = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
})

tabla_probabilidad = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
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

# --- Función para clasificar criticidad y color ---
def clasificar_criticidad(valor):
    if valor <= 0.7:
        return "Aceptable", "#008000"  # Verde
    elif valor <= 3:
        return "Tolerable", "#FFD700"  # Amarillo
    elif valor <= 7:
        return "Inaceptable", "#FF8C00"  # Naranja
    else:
        return "Inadmisible", "#FF0000"  # Rojo

# --- Función cálculo de riesgo ---
def calcular_riesgo(probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto):
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

# --- Estado para almacenar riesgos ---
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control", "Impacto", "Amenaza Inherente", "Amenaza Residual",
        "Amenaza Residual Ajustada", "Riesgo Residual", "Clasificación", "Color"
    ])

# --- Sidebar para idioma ---
with st.sidebar:
    idioma = st.selectbox("Idioma / Language", ["es", "en"], index=0)

t = textos[idioma]

# --- Layout principal ---
st.title("Calculadora de Riesgos" if idioma == "es" else "Risk Calculator")

with st.form("form_riesgo", clear_on_submit=False):
    nombre_riesgo = st.text_input(t["nombre_riesgo"])
    descripcion = st.text_area(t["descripcion_riesgo"])

    # Tipo impacto - desplegable con Código y nombre
    opciones_impacto = tabla_tipo_impacto.apply(lambda r: f"{r['Código']} - {r['Tipo de Impacto']}", axis=1).tolist()
    seleccion_impacto = st.selectbox(t["tipo_impacto"], opciones_impacto)
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    justificacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Justificación"].values[0]
    ponderacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Ponderación"].values[0]
    st.markdown(f"**{t['justificacion']}:** {justificacion_impacto}")

    # Exposición
    exposicion = st.selectbox(
        t["factor_exposicion"],
        options=tabla_exposicion["Factor"],
        format_func=lambda x: f"{x} {tabla_exposicion.loc[tabla_exposicion['Factor']==x,'Nivel'].values[0]}"
    )
    # Probabilidad
    probabilidad = st.selectbox(
        t["factor_probabilidad"],
        options=tabla_probabilidad["Factor"],
        format_func=lambda x: f"{x} {tabla_probabilidad.loc[tabla_probabilidad['Factor']==x,'Nivel'].values[0]}"
    )
    # Amenaza deliberada
    amenaza_deliberada = st.selectbox(
        t["amenaza_deliberada"],
        options=[1, 2, 3],
        format_func=lambda x: t["amenaza_deliberada_opciones"][x],
        index=0
    )
    # Efectividad control
    efectividad = st.slider(t["efectividad_control"], 0, 100, 50)
    efectividad_norm = efectividad / 100

    # Impacto
    impacto = st.selectbox(
        t["impacto"],
        options=tabla_impacto["Nivel"],
        format_func=lambda x: f"{x} - {tabla_impacto.loc[tabla_impacto['Nivel'] == x, 'Descripcion'].values[0]}"
    )
    valor_impacto = tabla_impacto.loc[tabla_impacto["Nivel"] == impacto, "Valor"].values[0]

    # Calcular riesgos
    amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual = calcular_riesgo(
        probabilidad, exposicion, amenaza_deliberada, efectividad_norm, valor_impacto, ponderacion_impacto
    )
    clasificacion, color = clasificar_criticidad(riesgo_residual)

    # Mostrar resultados
    st.markdown("### Resultados:")
    st.write(f"Amenaza Inherente: {amenaza_inherente:.4f}")
    st.write(f"Amenaza Residual: {amenaza_residual:.4f}")
    st.write(f"Amenaza Residual Ajustada: {amenaza_residual_ajustada:.4f}")
    st.write(f"Riesgo Residual: {riesgo_residual:.4f}")
    st.markdown(f"**Clasificación:** <span style='color:{color};font-weight:bold'>{clasificacion}</span>", unsafe_allow_html=True)

    # Botón agregar riesgo
    agregar = st.form_submit_button(t["agregar_riesgo"])

if agregar and nombre_riesgo.strip():
    nuevo = {
        "Nombre Riesgo": nombre_riesgo.strip(),
        "Descripción": descripcion.strip(),
        "Tipo Impacto": codigo_impacto,
        "Exposición": exposicion,
        "Probabilidad": probabilidad,
        "Amenaza Deliberada": amenaza_deliberada,
        "Efectividad Control": efectividad_norm,
        "Impacto": impacto,
        "Amenaza Inherente": amenaza_inherente,
        "Amenaza Residual": amenaza_residual,
        "Amenaza Residual Ajustada": amenaza_residual_ajustada,
        "Riesgo Residual": riesgo_residual,
        "Clasificación": clasificacion,
        "Color": color
    }
    st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo])], ignore_index=True)
    st.success(t["exito_agregar"])

# --- Mostrar mapa de calor y Pareto si hay riesgos ---
if not st.session_state.riesgos.empty:
    st.header(t["mapa_calor_titulo"])

    # Pivot para heatmap: index Tipo Impacto, columnas Probabilidad (factor), valor = amenaza residual * valor impacto ponderado
    df = st.session_state.riesgos.copy()
    df["Valor Mapa"] = df["Amenaza Residual"] * df.apply(
        lambda row: tabla_impacto.loc[tabla_impacto["Nivel"] == row["Impacto"], "Valor"].values[0]
        * tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == row["Tipo Impacto"], "Ponderación"].values[0] / 100,
        axis=1
    )

    matriz_calor = df.pivot_table(
        index="Tipo Impacto",
        columns="Probabilidad",
        values="Valor Mapa",
        aggfunc=np.mean
    ).fillna(0).sort_index()

    colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]
    cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(
        matriz_calor,
        annot=True,
        fmt=".2f",
        cmap=cmap,
        cbar_kws={"label": t["mapa_calor_titulo"]},
        linewidths=0.5,
        linecolor='gray'
    )
    ax.set_xlabel(t["factor_probabilidad"])
    ax.set_ylabel(t["tipo_impacto"])
    st.pyplot(fig)

    # Pareto
    st.header(t["pareto_titulo"])
    df_pareto = df.sort_values(by="Riesgo Residual", ascending=False)
    df_pareto["% Riesgo"] = 100 * df_pareto["Riesgo Residual"] / df_pareto["Riesgo Residual"].sum()
    df_pareto["% Acumulado"] = df_pareto["% Riesgo"].cumsum()

    fig2, ax1 = plt.subplots(figsize=(10,5))
    ax1.bar(df_pareto["Nombre Riesgo"], df_pareto["% Riesgo"], color='skyblue')
    ax1.set_ylabel("% Riesgo Individual" if idioma=="es" else "% Individual Risk", color='blue')
    ax1.set_xticklabels(df_pareto["Nombre Riesgo"], rotation=45, ha='right')

    ax2 = ax1.twinx()
    ax2.plot(df_pareto["Nombre Riesgo"], df_pareto["% Acumulado"], color='red', marker='o')
    ax2.set_ylabel("% Riesgo Acumulado" if idioma=="es" else "% Cumulative Risk", color='red')
    ax2.axhline(80, color='gray', linestyle='--')
    ax2.text(len(df_pareto)*0.75, 82, "80% Línea de Pareto" if idioma=="es" else "80% Pareto Line", color='gray')

    plt.tight_layout()
    st.pyplot(fig2)

    # Mostrar matriz acumulativa
    st.header(t["matriz_acumulativa_titulo"])
    st.dataframe(df.style.apply(
        lambda x: ["background-color: "+x["Color"] if col=="Color" else "" for col in df.columns], axis=1
    ))

    # Botón descarga Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Matriz de Riesgos', index=False)
    st.download_button(
        label=t["descargar_excel"],
        data=output.getvalue(),
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info(t["info_agrega_riesgos"])

