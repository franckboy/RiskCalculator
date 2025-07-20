import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

# Traducciones para la app
idiomas = {
    "es": {
        "titulo": "Calculadora de Riesgos",
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion": "Descripción del riesgo",
        "tipo_impacto": "Tipo de Impacto",
        "exposicion": "Factor de Exposición",
        "probabilidad": "Factor de Probabilidad",
        "amenaza_deliberada": "Amenaza Deliberada",
        "efectividad": "Efectividad del control (%)",
        "impacto": "Impacto",
        "agregar": "Agregar riesgo a la matriz",
        "tablas_fijas": {
            "efectividad": "Efectividad de Controles",
            "exposicion": "Factor de Exposición",
            "probabilidad": "Factor de Probabilidad",
            "impacto": "Impacto / Severidad",
            "criticidad": "Índice de Criticidad"
        },
        "resultados": "Resultados:",
        "amenaza_inherente": "Amenaza Inherente",
        "amenaza_residual": "Amenaza Residual",
        "amenaza_residual_ajustada": "Amenaza Residual Ajustada (x Amenaza Deliberada)",
        "riesgo_residual": "Riesgo Residual",
        "clasificacion": "Clasificación",
        "color": "Color",
        "mapa_calor": "Mapa de Calor por Tipo de Impacto y Probabilidad x Impacto",
        "matriz_acumulativa": "Matriz Acumulativa de Riesgos",
        "descargar_excel": "Descargar matriz de riesgos en Excel",
        "idioma": "Idioma",
        "justificaciones": {
            "H": "Afecta directamente la vida, salud o integridad de las personas. Prioridad máxima según ISO 45001.",
            "A": "Daños ecológicos pueden ser irreversibles y conllevan sanciones graves. ISO 14001.",
            "E": "Pérdidas financieras afectan continuidad y viabilidad del negocio. COSO ERM.",
            "O": "Interrumpe procesos críticos, producción o servicios clave. ISO 22301.",
            "I": "Daño físico a instalaciones o activos afecta operaciones y seguridad.",
            "T": "Fallas de sistemas o ciberataques afectan datos y procesos. ISO 27005.",
            "R": "Afecta imagen pública, confianza y puede derivar en sanciones indirectas. COSO ERM.",
            "S": "Impacta comunidades, condiciones laborales o responsabilidad social. ISO 26000.",
            "C": "Pérdida de clientes, contratos o mercado. Es recuperable pero afecta ingresos."
        }
    },
    "en": {
        "titulo": "Risk Calculator",
        "nombre_riesgo": "Risk Name",
        "descripcion": "Risk Description",
        "tipo_impacto": "Impact Type",
        "exposicion": "Exposure Factor",
        "probabilidad": "Probability Factor",
        "amenaza_deliberada": "Deliberate Threat",
        "efectividad": "Control Effectiveness (%)",
        "impacto": "Impact",
        "agregar": "Add risk to matrix",
        "tablas_fijas": {
            "efectividad": "Control Effectiveness",
            "exposicion": "Exposure Factor",
            "probabilidad": "Probability Factor",
            "impacto": "Impact / Severity",
            "criticidad": "Criticality Index"
        },
        "resultados": "Results:",
        "amenaza_inherente": "Inherent Threat",
        "amenaza_residual": "Residual Threat",
        "amenaza_residual_ajustada": "Adjusted Residual Threat (x Deliberate Threat)",
        "riesgo_residual": "Residual Risk",
        "clasificacion": "Classification",
        "color": "Color",
        "mapa_calor": "Heatmap by Impact Type and Probability x Impact",
        "matriz_acumulativa": "Cumulative Risk Matrix",
        "descargar_excel": "Download risk matrix in Excel",
        "idioma": "Language",
        "justificaciones": {
            "H": "Directly affects life, health or integrity of people. Highest priority per ISO 45001.",
            "A": "Ecological damage can be irreversible and lead to severe sanctions. ISO 14001.",
            "E": "Financial losses affect business continuity and viability. COSO ERM.",
            "O": "Disrupts critical processes, production or key services. ISO 22301.",
            "I": "Physical damage to facilities or assets affects operations and safety.",
            "T": "System failures or cyberattacks affect data and processes. ISO 27005.",
            "R": "Affects public image, trust and may result in indirect sanctions. COSO ERM.",
            "S": "Impacts communities, working conditions or social responsibility. ISO 26000.",
            "C": "Loss of clients, contracts or market. Recoverable but affects income."
        }
    }
}

# Selección de idioma
idioma_actual = st.selectbox("🌐 " + "Idioma / Language", options=["Español", "English"], index=0)
lang = "es" if idioma_actual == "Español" else "en"
t = idiomas[lang]

# --- Tablas fijas para referencia ---
tabla_efectividad = pd.DataFrame({
    "Rango": ["0%", "1 - 20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
    "Factor": [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.1],
    "Mitigacion": [
        "Inefectiva",
        "Reduce solo en condiciones ideales",
        "Mitiga riesgos menores.",
        "Control estándar con limitaciones.",
        "Reduce significativamente el riesgo",
        "Control robusto y bien implementado.",
        "Elimina casi todo el riesgo"
    ] if lang == "es" else [
        "Ineffective",
        "Reduces only under ideal conditions",
        "Mitigates minor risks.",
        "Standard control with limitations.",
        "Significantly reduces risk",
        "Robust and well implemented control.",
        "Eliminates almost all risk"
    ],
    "Descripcion": [
        "No reduce el riesgo",
        "Reduce solo en condiciones ideales",
        "Mitiga riesgos menores.",
        "Control estándar con limitaciones.",
        "Reduce significativamente el riesgo",
        "Control robusto y bien implementado.",
        "Elimina casi todo el riesgo"
    ] if lang == "es" else [
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
    "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"] if lang == "es" else ["Very Low", "Low", "Moderate", "High", "Very High"],
    "Descripcion": [
        "Exposición extremadamente rara",
        "Exposición ocasional (cada 10 años)",
        "Exposición algunas veces al año",
        "Exposición mensual",
        "Exposición frecuente o semanal"
    ] if lang == "es" else [
        "Extremely rare exposure",
        "Occasional exposure (every 10 years)",
        "Exposure a few times per year",
        "Monthly exposure",
        "Frequent or weekly exposure"
    ]
})

tabla_probabilidad = pd.DataFrame({
    "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
    "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"] if lang == "es" else ["Very Low", "Low", "Moderate", "High", "Very High"],
    "Descripcion": [
        "En condiciones excepcionales",
        "Ha sucedido alguna vez",
        "Podría ocurrir ocasionalmente",
        "Probable en ocasiones",
        "Ocurre con frecuencia / inminente"
    ] if lang == "es" else [
        "Under exceptional conditions",
        "Has happened once",
        "Might happen occasionally",
        "Likely sometimes",
        "Happens frequently / imminent"
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
    ] if lang == "es" else [
        "No significant effect",
        "Minor effect",
        "Partial and temporary effect",
        "Significant effect",
        "Serious impact or total loss"
    ]
})

tabla_criticidad = pd.DataFrame({
    "Límite Superior": [2, 4, 15, float('inf')],
    "Clasificación": ["ACEPTABLE", "TOLERABLE", "INACEPTABLE", "INADMISIBLE"] if lang == "es" else ["ACCEPTABLE", "TOLERABLE", "UNACCEPTABLE", "INTOLERABLE"],
    "Color": ["Verde", "Amarillo", "Naranja", "Rojo"] if lang == "es" else ["Green", "Yellow", "Orange", "Red"]
})

colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]
cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

def clasificar_criticidad(valor):
    if valor <= 2:
        return tabla_criticidad.loc[0, "Clasificación"], tabla_criticidad.loc[0, "Color"]
    elif valor <= 4:
        return tabla_criticidad.loc[1, "Clasificación"], tabla_criticidad.loc[1, "Color"]
    elif valor <= 15:
        return tabla_criticidad.loc[2, "Clasificación"], tabla_criticidad.loc[2, "Color"]
    else:
        return tabla_criticidad.loc[3, "Clasificación"], tabla_criticidad.loc[3, "Color"]

# Ponderaciones y justificaciones por tipo de impacto
ponderaciones_impacto = {
    "Humano": 100,
    "Ambiental": 85,
    "Económico": 80,
    "Operacional": 75,
    "Infraestructura": 65,
    "Tecnológico": 60,
    "Reputacional": 50,
    "Social": 45,
    "Comercial": 40
}

justificaciones_impacto = t["justificaciones"]

def mostrar_tabla_fija(df, titulo):
    st.markdown(f"### {titulo}")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True, filter=False, sortable=False)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, height=min(200, 35*len(df)), fit_columns_on_grid_load=True, enable_enterprise_modules=False, update_mode='NO_UPDATE')

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Justificación Impacto",
        "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", 
        "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada", "Riesgo Residual",
        "Clasificación Criticidad", "Color Criticidad"
    ])

# Layout principal
col_izq, col_centro, col_der = st.columns([1.3, 2, 2])

with col_izq:
    mostrar_tabla_fija(tabla_efectividad[["Rango", "Mitigacion", "Descripcion"]], t["tablas_fijas"]["efectividad"])
    mostrar_tabla_fija(tabla_exposicion[["Factor", "Nivel", "Descripcion"]], t["tablas_fijas"]["exposicion"])
    mostrar_tabla_fija(tabla_probabilidad[["Factor", "Nivel", "Descripcion"]], t["tablas_fijas"]["probabilidad"])
    mostrar_tabla_fija(tabla_impacto[["Nivel", "Valor", "Descripcion"]], t["tablas_fijas"]["impacto"])
    st.markdown(f"### {t['tablas_fijas']['criticidad']}")
    crit_display = tabla_criticidad.drop(columns=["Color"])
    st.table(crit_display)
    st.markdown("""
        <ul>
            <li style='color:green;'>Verde: Aceptable (≤ 2)</li>
            <li style='color:gold;'>Amarillo: Tolerable (≤ 4)</li>
            <li style='color:orange;'>Naranja: Inaceptable (≤ 15)</li>
            <li style='color:red;'>Rojo: Inadmisible (> 15)</li>
        </ul>
    """, unsafe_allow_html=True)

with col_centro:
    st.title(t["titulo"])
    st.subheader(t["titulo"])

    nombre_riesgo = st.text_input(t["nombre_riesgo"])
    descripcion = st.text_area(t["descripcion"])
    tipo_impacto = st.selectbox(
        t["tipo_impacto"],
        options=list(ponderaciones_impacto.keys()),
        format_func=lambda x: f"{x} - {justificaciones_impacto.get(x[0], '') if x in justificaciones_impacto else ''}"
    )
    exposicion = st.selectbox(t["exposicion"], options=tabla_exposicion["Factor"], format_func=lambda x: f"{x} - {tabla_exposicion.loc[tabla_exposicion['Factor'] == x, 'Nivel'].values[0]}")
    probabilidad = st.selectbox(t["probabilidad"], options=tabla_probabilidad["Factor"], format_func=lambda x: f"{x} - {tabla_probabilidad.loc[tabla_probabilidad['Factor'] == x, 'Nivel'].values[0]}")
    amenaza_deliberada = st.selectbox(t["amenaza_deliberada"], options=[1, 2, 3], format_func=lambda x: {1: "Baja" if lang == "es" else "Low", 2: "Intermedia" if lang == "es" else "Medium", 3: "Alta" if lang == "es" else "High"}[x], index=0)
    efectividad = st.slider(t["efectividad"], 0, 100, 50)
    impacto = st.selectbox(
        t["impacto"],
        options=tabla_impacto["Nivel"],
        format_func=lambda x: f"{x} - {tabla_impacto.loc[tabla_impacto['Nivel'] == x, 'Descripcion'].values[0]}"
    )

    # Cálculos
    efec_norm = efectividad / 100
    amenaza_inherente = round(exposicion * probabilidad, 4)
    amenaza_residual = round(amenaza_inherente * (1 - efec_norm), 4)
    amenaza_residual_ajustada = round(amenaza_residual * amenaza_deliberada, 4)

    # Ajustar riesgo residual con ponderación del tipo de impacto (escala 0 a 1)
    ponderacion_impacto = ponderaciones_impacto.get(tipo_impacto, 40) / 100
    riesgo_residual = round(amenaza_residual_ajustada * tabla_impacto.loc[tabla_impacto["Nivel"] == impacto, "Valor"].values[0] * ponderacion_impacto, 4)

    clasificacion, color = clasificar_criticidad(riesgo_residual)

    # Mostrar justificación del tipo de impacto
    justificacion_impacto = justificaciones_impacto.get(tipo_impacto[0], "")

    st.markdown(f"### {t['resultados']}")
    st.write(f"- {t['amenaza_inherente']}: {amenaza_inherente}")
    st.write(f"- {t['amenaza_residual']}: {amenaza_residual}")
    st.write(f"- {t['amenaza_residual_ajustada']}: {amenaza_residual_ajustada}")
    st.write(f"- {t['riesgo_residual']}: {riesgo_residual}")
    st.write(f"- {t['clasificacion']}: **{clasificacion}** (Color: {color})")
    st.write(f"- Justificación del Tipo de Impacto: {justificacion_impacto}")

    if st.button(t["agregar"]) and nombre_riesgo.strip() != "":
        nuevo_riesgo = {
            "Nombre Riesgo": nombre_riesgo.strip(),
            "Descripción": descripcion.strip(),
            "Tipo Impacto": tipo_impacto,
            "Justificación Impacto": justificacion_impacto,
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
        st.success("Riesgo agregado a la matriz acumulativa.")

with col_der:
    # Mapa de calor y gráficos arriba
    st.header(t["mapa_calor"])
    if not st.session_state.riesgos.empty:
        st.session_state.riesgos["Probabilidad x Impacto"] = st.session_state.riesgos["Probabilidad"] * st.session_state.riesgos["Impacto"]

        pivot_heatmap = st.session_state.riesgos.pivot_table(
            index="Tipo Impacto",
            values="Probabilidad x Impacto",
            aggfunc=np.sum
        ).sort_values(ascending=False)

        # Mostrar tabla resumen de heatmap
        st.dataframe(pivot_heatmap.to_frame())

        # Gráfico de barras del mapa de calor
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.barplot(x=pivot_heatmap.index, y=pivot_heatmap.values, palette="Reds", ax=ax)
        ax.set_ylabel("Probabilidad x Impacto")
        ax.set_xlabel(t["tipo_impacto"])
        ax.set_title(t["mapa_calor"])
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Diagrama de Pareto para priorización
        st.header("Diagrama de Pareto - Prioridad de Riesgos")
        riesgos_sorted = st.session_state.riesgos.sort_values(by="Riesgo Residual", ascending=False)
        riesgos_sorted["Cumulative"] = riesgos_sorted["Riesgo Residual"].cumsum()
        riesgos_sorted["Porcentaje Cumulativo"] = 100 * riesgos_sorted["Cumulative"] / riesgos_sorted["Riesgo Residual"].sum()

        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.bar(riesgos_sorted["Nombre Riesgo"], riesgos_sorted["Riesgo Residual"], color="skyblue")
        ax2.set_ylabel("Riesgo Residual")
        ax2.set_xlabel("Riesgo")
        ax2.set_title("Diagrama de Pareto de Riesgos")
        ax2.tick_params(axis="x", rotation=90)

        ax22 = ax2.twinx()
        ax22.plot(riesgos_sorted["Nombre Riesgo"], riesgos_sorted["Porcentaje Cumulativo"], color="red", marker="o")
        ax22.set_ylabel("Porcentaje Cumulativo (%)")

        st.pyplot(fig2)
    else:
        st.info("Agrega riesgos para visualizar el mapa de calor y el diagrama de Pareto.")

# Matriz acumulativa abajo de todo (anchura completa)
st.markdown(f"## {t['matriz_acumulativa']}")
if not st.session_state.riesgos.empty:
    st.dataframe(st.session_state.riesgos.style.applymap(
        lambda x: 'background-color: '+ {
            "Verde": "#008000",
            "Amarillo": "#FFD700",
            "Naranja": "#FF8C00",
            "Rojo": "#FF0000"
        }.get(x, "") if isinstance(x, str) else ""
    , subset=["Color Criticidad"]))
else:
    st.info("No hay riesgos agregados aún.")

# Botón para exportar Excel (sin writer.save())
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Matriz de Riesgos')
    writer.save = lambda : None  # Sobrescribimos para evitar error
    writer.close()
    processed_data = output.getvalue()
    return processed_data

if not st.session_state.riesgos.empty:
    excel_data = to_excel(st.session_state.riesgos)
    st.download_button(
        label=t["descargar_excel"],
        data=excel_data,
        file_name='matriz_riesgos.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


