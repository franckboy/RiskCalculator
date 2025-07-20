import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from st_aggrid import AgGrid, GridOptionsBuilder
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap

st.set_page_config(layout="wide")

# Textos multilenguaje completos para UI y listas
textos = {
    "es": {
        "titulo": "Calculadora de Riesgos",
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion": "Descripción del riesgo",
        "tipo_impacto": "Tipo de Impacto",
        "factor_exposicion": "Factor de Exposición",
        "factor_probabilidad": "Factor de Probabilidad",
        "amenaza_deliberada": "Amenaza Deliberada",
        "efectividad_control": "Efectividad del control (%)",
        "impacto_nivel": "Impacto (nivel 1-5)",
        "resultados": "Resultados",
        "agregar": "Agregar riesgo a la matriz",
        "mapa_calor_grafico": "Mapa de Calor y Gráficos",
        "diagrama_pareto": "Diagrama de Pareto",
        "matriz_acumulativa": "Matriz Acumulativa de Riesgos",
        "descargar_excel": "Descargar matriz de riesgos en Excel",
        "sin_riesgos": "Agrega riesgos para mostrar la matriz acumulativa.",
        "sin_graficos": "Agrega riesgos para mostrar mapa de calor y gráficos.",
        "exposicion_niveles": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
        "probabilidad_niveles": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
        "amenaza_niveles": ["Baja", "Intermedia", "Alta"],
        "impacto_niveles": ["1 - No afecta significativamente", "2 - Afectación menor", "3 - Afectación parcial y temporal", "4 - Afectación significativa", "5 - Impacto serio o pérdida total"],
        "tipos_impacto": {
            "H": ("Humano", "Afecta directamente la vida, salud o integridad de las personas. Prioridad máxima según ISO 45001."),
            "A": ("Ambiental", "Daños ecológicos pueden ser irreversibles y conllevan sanciones graves. ISO 14001."),
            "E": ("Económico", "Pérdidas financieras afectan continuidad y viabilidad del negocio. COSO ERM."),
            "O": ("Operacional", "Interrumpe procesos críticos, producción o servicios clave. ISO 22301."),
            "I": ("Infraestructura", "Daño físico a instalaciones o activos afecta operaciones y seguridad."),
            "T": ("Tecnológico", "Fallas de sistemas o ciberataques afectan datos y procesos. ISO 27005."),
            "R": ("Reputacional", "Afecta imagen pública, confianza y puede derivar en sanciones indirectas. COSO ERM."),
            "S": ("Social", "Impacta comunidades, condiciones laborales o responsabilidad social. ISO 26000."),
            "C": ("Comercial", "Pérdida de clientes, contratos o mercado. Es recuperable pero afecta ingresos.")
        }
    },
    "en": {
        "titulo": "Risk Calculator",
        "nombre_riesgo": "Risk Name",
        "descripcion": "Risk Description",
        "tipo_impacto": "Type of Impact",
        "factor_exposicion": "Exposure Factor",
        "factor_probabilidad": "Probability Factor",
        "amenaza_deliberada": "Deliberate Threat",
        "efectividad_control": "Control Effectiveness (%)",
        "impacto_nivel": "Impact (level 1-5)",
        "resultados": "Results",
        "agregar": "Add risk to matrix",
        "mapa_calor_grafico": "Heatmap and Charts",
        "diagrama_pareto": "Pareto Chart",
        "matriz_acumulativa": "Cumulative Risk Matrix",
        "descargar_excel": "Download risk matrix Excel",
        "sin_riesgos": "Add risks to display the cumulative matrix.",
        "sin_graficos": "Add risks to display heatmap and charts.",
        "exposicion_niveles": ["Very Low", "Low", "Moderate", "High", "Very High"],
        "probabilidad_niveles": ["Very Low", "Low", "Moderate", "High", "Very High"],
        "amenaza_niveles": ["Low", "Medium", "High"],
        "impacto_niveles": ["1 - No significant effect", "2 - Minor impact", "3 - Partial and temporary impact", "4 - Significant impact", "5 - Serious impact or total loss"],
        "tipos_impacto": {
            "H": ("Human", "Directly affects life, health, or integrity of people. Highest priority per ISO 45001."),
            "A": ("Environmental", "Ecological damage can be irreversible with severe penalties. ISO 14001."),
            "E": ("Economic", "Financial losses affect business continuity and viability. COSO ERM."),
            "O": ("Operational", "Interrupts critical processes, production or key services. ISO 22301."),
            "I": ("Infrastructure", "Physical damage to facilities or assets affects operations and safety."),
            "T": ("Technological", "System failures or cyberattacks affect data and processes. ISO 27005."),
            "R": ("Reputational", "Affects public image, trust, and may lead to indirect penalties. COSO ERM."),
            "S": ("Social", "Impacts communities, labor conditions or social responsibility. ISO 26000."),
            "C": ("Commercial", "Loss of customers, contracts or market. Recoverable but affects income.")
        }
    }
}

# Datos técnicos (factores numéricos, fijos)
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

factores_exposicion = [0.05, 0.15, 0.30, 0.55, 0.85]
factores_probabilidad = [0.05, 0.15, 0.30, 0.55, 0.85]

# Funciones auxiliares
def clasificar_criticidad(valor):
    if valor <= 2:
        return "ACEPTABLE", "#008000"
    elif valor <= 4:
        return "TOLERABLE", "#FFD700"
    elif valor <= 15:
        return "INACEPTABLE", "#FF8C00"
    else:
        return "INADMISIBLE", "#FF0000"

def mostrar_tabla_fija(df, titulo):
    st.markdown(f"### {titulo}")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True, filter=False, sortable=False)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, height=min(250, 35*len(df)), fit_columns_on_grid_load=True, enable_enterprise_modules=False, update_mode='NO_UPDATE')

# Aplicación

idioma = st.selectbox("Selecciona idioma / Select Language", options=["es", "en"], index=0)
t = textos[idioma]

# Prepara tablas fijas con traducción para exposición, probabilidad, amenaza deliberada e impacto
tabla_exposicion = pd.DataFrame({
    "Factor": factores_exposicion,
    "Nivel": t["exposicion_niveles"],
    "Descripcion": ["" for _ in factores_exposicion]
})

tabla_probabilidad = pd.DataFrame({
    "Factor": factores_probabilidad,
    "Nivel": t["probabilidad_niveles"],
    "Descripcion": ["" for _ in factores_probabilidad]
})

# Amenaza deliberada opciones con traducción
opciones_amenaza = {1:t["amenaza_niveles"][0], 2:t["amenaza_niveles"][1], 3:t["amenaza_niveles"][2]}

# Impacto niveles traducidos
impacto_niveles_opciones = t["impacto_niveles"]

# Tipos impacto traducidos y con justificación
tipos_codigo = list(t["tipos_impacto"].keys())
tipos_nombre = [v[0] for v in t["tipos_impacto"].values()]
tipos_justificacion = [v[1] for v in t["tipos_impacto"].values()]

tabla_impacto = pd.DataFrame({
    "Codigo": tipos_codigo,
    "Tipo": tipos_nombre,
    "Justificacion": tipos_justificacion
})

# Tablas fijas técnicas (sin traducir)
tabla_efectividad_static = tabla_efectividad.copy()

# Inicializar DataFrame en sesión
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Tipo Impacto",
        "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada", "Riesgo Residual",
        "Clasificación Criticidad", "Color Criticidad"
    ])

col_izq, col_centro, col_der = st.columns([1.2, 2, 1.5])

with col_izq:
    mostrar_tabla_fija(tabla_efectividad_static[["Rango", "Mitigacion", "Descripcion"]], "Efectividad de Controles")
    mostrar_tabla_fija(tabla_exposicion[["Factor", "Nivel", "Descripcion"]], t["factor_exposicion"])
    mostrar_tabla_fija(tabla_probabilidad[["Factor", "Nivel", "Descripcion"]], t["factor_probabilidad"])
    mostrar_tabla_fija(tabla_impacto[["Codigo", "Tipo", "Justificacion"]], t["tipo_impacto"])

with col_centro:
    st.title(t["titulo"])
    st.subheader(t["titulo"])

    nombre_riesgo = st.text_input(t["nombre_riesgo"])
    descripcion = st.text_area(t["descripcion"])

    tipo_impacto_sel = st.selectbox(
        t["tipo_impacto"],
        options=tabla_impacto["Tipo"],
        format_func=lambda x: f"{x} - {tabla_impacto.loc[tabla_impacto['Tipo']==x, 'Justificacion'].values[0]}"
    )

    exposicion_sel = st.selectbox(
        t["factor_exposicion"],
        options=tabla_exposicion["Factor"],
        format_func=lambda x: f"{x} - {tabla_exposicion.loc[tabla_exposicion['Factor']==x, 'Nivel'].values[0]}"
    )

    probabilidad_sel = st.selectbox(
        t["factor_probabilidad"],
        options=tabla_probabilidad["Factor"],
        format_func=lambda x: f"{x} - {tabla_probabilidad.loc[tabla_probabilidad['Factor']==x, 'Nivel'].values[0]}"
    )

    amenaza_deliberada_sel = st.selectbox(
        t["amenaza_deliberada"],
        options=[1, 2, 3],
        format_func=lambda x: opciones_amenaza[x]
    )

    efectividad = st.slider(t["efectividad_control"], 0, 100, 50)

    impacto_nivel_sel = st.selectbox(t["impacto_nivel"], options=[1, 2, 3, 4, 5], format_func=lambda x: impacto_niveles_opciones[x-1])

    # Cálculos
    efec_norm = efectividad / 100
    amenaza_inherente = round(exposicion_sel * probabilidad_sel, 4)
    amenaza_residual = round(amenaza_inherente * (1 - efec_norm), 4)
    amenaza_residual_ajustada = round(amenaza_residual * amenaza_deliberada_sel, 4)

    # Obtener ponderación para tipo impacto
    ponderacion_impacto = tabla_impacto.loc[tabla_impacto["Tipo"] == tipo_impacto_sel, "Codigo"].map({
        "H": 100, "A": 85, "E": 80, "O": 75, "I": 65, "T": 60, "R": 50, "S": 45, "C": 40
    })

    # Si no encuentra la ponderación (por alguna razón), valor por defecto 50
    if ponderacion_impacto.empty:
        ponderacion = 50
    else:
        ponderacion = ponderacion_impacto.values[0]

    impacto_valor_base = [5, 10, 30, 60, 85][impacto_nivel_sel-1]
    impacto_valor_ajustado = impacto_valor_base * (ponderacion / 100)

    riesgo_residual = round(amenaza_residual_ajustada * impacto_valor_ajustado, 4)
    clasificacion, color = clasificar_criticidad(riesgo_residual)

    st.markdown(f"### {t['resultados']}")
    st.write(f"- Amenaza Inherente: {amenaza_inherente}")
    st.write(f"- Amenaza Residual: {amenaza_residual}")
    st.write(f"- Amenaza Residual Ajustada (x Amenaza Deliberada): {amenaza_residual_ajustada}")
    st.write(f"- Valor Impacto Base: {impacto_valor_base}")
    st.write(f"- Ponderación Tipo Impacto: {ponderacion}")
    st.write(f"- Valor Impacto Ajustado: {impacto_valor_ajustado}")
    st.write(f"- Riesgo Residual: {riesgo_residual}")
    st.write(f"- Clasificación: **{clasificacion}** (Color: {color})")

    if st.button(t["agregar"]) and nombre_riesgo.strip() != "":
        nuevo_riesgo = {
            "Nombre Riesgo": nombre_riesgo.strip(),
            "Descripción": descripcion.strip(),
            "Exposición": exposicion_sel,
            "Probabilidad": probabilidad_sel,
            "Amenaza Deliberada": amenaza_deliberada_sel,
            "Efectividad Control (%)": efectividad,
            "Impacto": impacto_nivel_sel,
            "Tipo Impacto": tipo_impacto_sel,
            "Amenaza Inherente": amenaza_inherente,
            "Amenaza Residual": amenaza_residual,
            "Amenaza Residual Ajustada": amenaza_residual_ajustada,
            "Riesgo Residual": riesgo_residual,
            "Clasificación Criticidad": clasificacion,
            "Color Criticidad": color
        }
        st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
        st.success(t["agregar"] + " exitoso!")

with col_der:
    st.header(t["mapa_calor_grafico"])
    if not st.session_state.riesgos.empty:
        st.session_state.riesgos["Impacto Valor"] = st.session_state.riesgos["Impacto"].map(
            lambda x: [5, 10, 30, 60, 85][int(x)-1]
        )
        st.session_state.riesgos["Probabilidad x Impacto"] = st.session_state.riesgos["Probabilidad"] * st.session_state.riesgos["Impacto Valor"]

        matriz_calor = st.session_state.riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Probabilidad",
            values="Probabilidad x Impacto",
            aggfunc=np.mean
        ).fillna(0).sort_index()

        colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]
        cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

        fig, ax = plt.subplots(figsize=(7,5))
        sns.heatmap(
            matriz_calor,
            annot=True,
            fmt=".2f",
            cmap=cmap,
            cbar_kws={"label": t["factor_probabilidad"]}
        )
        ax.set_xlabel(t["factor_probabilidad"])
        ax.set_ylabel(t["tipo_impacto"])
        st.pyplot(fig)

        # Diagrama de Pareto
        st.header(t["diagrama_pareto"])
        df_pareto = st.session_state.riesgos.sort_values(by="Riesgo Residual", ascending=False).copy()
        df_pareto["Contribucion"] = df_pareto["Riesgo Residual"] / df_pareto["Riesgo Residual"].sum()
        df_pareto["Acumulado"] = df_pareto["Contribucion"].cumsum()

        fig2, ax2 = plt.subplots(figsize=(8,4))
        ax2.bar(df_pareto["Nombre Riesgo"], df_pareto["Contribucion"], color="C0")
        ax2.set_ylabel("Contribución individual", color="C0")
        ax2.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax2.tick_params(axis='y', labelcolor="C0")
        ax2.set_xticklabels(df_pareto["Nombre Riesgo"], rotation=45, ha="right", fontsize=9)

        ax3 = ax2.twinx()
        ax3.plot(df_pareto["Nombre Riesgo"], df_pareto["Acumulado"], color="C1", marker="D", ms=5)
        ax3.set_ylabel("Contribución acumulada", color="C1")
        ax3.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        ax3.tick_params(axis='y', labelcolor="C1")
        ax3.grid(False)

        st.pyplot(fig2)
    else:
        st.info(t["sin_graficos"])

# Matriz acumulativa ancho completo abajo
st.markdown("---")
st.header(t["matriz_acumulativa"])

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
        writer.save()
    processed_data = output.getvalue()

    st.download_button(
        label=t["descargar_excel"],
        data=processed_data,
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info(t["sin_riesgos"])

