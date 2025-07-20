import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder
import matplotlib.ticker as mtick

st.set_page_config(layout="wide")

# Traducciones (ejemplo para español e inglés)
idiomas = {
    "es": {
        "efectividad_controles": "Efectividad de Controles",
        "factor_exposicion": "Factor de Exposición",
        "factor_probabilidad": "Factor de Probabilidad",
        "tipo_impacto": "Tipo de Impacto",
        "resultados": "Resultados",
        "agregar": "Agregar riesgo a la matriz",
        "mapa_calor_grafico": "Mapa de Calor por Tipo de Impacto y Probabilidad x Impacto",
        "diagrama_pareto": "Diagrama de Pareto de Riesgos",
        "sin_graficos": "Agrega riesgos para mostrar los gráficos.",
        "matriz_acumulativa": "Matriz Acumulativa de Riesgos",
        "descargar_excel": "Descargar matriz de riesgos en Excel",
        "sin_riesgos": "Agrega riesgos para mostrar la matriz acumulativa."
    },
    "en": {
        "efectividad_controles": "Effectiveness of Controls",
        "factor_exposicion": "Exposure Factor",
        "factor_probabilidad": "Probability Factor",
        "tipo_impacto": "Type of Impact",
        "resultados": "Results",
        "agregar": "Add risk to matrix",
        "mapa_calor_grafico": "Heatmap by Impact Type and Probability x Impact",
        "diagrama_pareto": "Risk Pareto Chart",
        "sin_graficos": "Add risks to display charts.",
        "matriz_acumulativa": "Cumulative Risk Matrix",
        "descargar_excel": "Download risk matrix as Excel",
        "sin_riesgos": "Add risks to display the cumulative matrix."
    }
}

# Selector idioma
idioma_sel = st.selectbox("Selecciona idioma / Select language", options=list(idiomas.keys()), index=0)
t = idiomas[idioma_sel]

# Tablas fijas
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
    "Codigo": ["H", "A", "E", "O", "I", "T", "R", "S", "C"],
    "Tipo": ["Humano", "Ambiental", "Económico", "Operacional", "Infraestructura", "Tecnológico", "Reputacional", "Social", "Comercial"],
    "Ponderacion": [100, 85, 80, 75, 65, 60, 50, 45, 40],
    "Justificacion": [
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

tabla_criticidad = pd.DataFrame({
    "Límite Superior": [2, 4, 15, float('inf')],
    "Clasificación": ["ACEPTABLE", "TOLERABLE", "INACEPTABLE", "INADMISIBLE"],
    "Color": ["Verde", "Amarillo", "Naranja", "Rojo"]
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

def mostrar_tabla_fija(df, titulo, key=None):
    st.markdown(f"### {titulo}")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True, filter=False, sortable=False)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()
    AgGrid(
        df,
        gridOptions=gridOptions,
        height=min(250, 35*len(df)),
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        update_mode='NO_UPDATE',
        key=key
    )

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto",
        "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada", "Riesgo Residual",
        "Clasificación Criticidad", "Color Criticidad"
    ])

# Layout columnas
col_izq, col_centro, col_der = st.columns([1.3, 2, 2])

with col_izq:
    mostrar_tabla_fija(tabla_efectividad[["Rango", "Mitigacion", "Descripcion"]], t["efectividad_controles"], key="tabla_efectividad")
    mostrar_tabla_fija(tabla_exposicion[["Factor", "Nivel", "Descripcion"]], t["factor_exposicion"], key="tabla_exposicion")
    mostrar_tabla_fija(tabla_probabilidad[["Factor", "Nivel", "Descripcion"]], t["factor_probabilidad"], key="tabla_probabilidad")
    mostrar_tabla_fija(tabla_impacto[["Codigo", "Tipo", "Justificacion"]], t["tipo_impacto"], key="tabla_impacto")

with col_centro:
    st.title("Calculadora de Riesgos")
    st.subheader("Datos del Riesgo")

    nombre_riesgo = st.text_input("Nombre del riesgo")
    descripcion = st.text_area("Descripción del riesgo")
    tipo_impacto = st.selectbox(
        t["tipo_impacto"],
        options=tabla_impacto["Tipo"],
        index=0
    )
    exposicion = st.selectbox(
        t["factor_exposicion"],
        options=tabla_exposicion["Factor"],
        format_func=lambda x: f"{x} - {tabla_exposicion.loc[tabla_exposicion['Factor']==x, 'Nivel'].values[0]}"
    )
    probabilidad = st.selectbox(
        t["factor_probabilidad"],
        options=tabla_probabilidad["Factor"],
        format_func=lambda x: f"{x} - {tabla_probabilidad.loc[tabla_probabilidad['Factor']==x, 'Nivel'].values[0]}"
    )
    amenaza_deliberada = st.selectbox(
        "Amenaza Deliberada",
        options=[1, 2, 3],
        format_func=lambda x: {1: "Baja", 2: "Intermedia", 3: "Alta"}[x],
        index=0
    )
    efectividad = st.slider("Efectividad del control (%)", 0, 100, 50)
    impacto_nivel = st.selectbox(
        "Impacto",
        options=tabla_impacto.index + 1,
        format_func=lambda x: f"{x} - {['No afecta significativamente','Afectación menor','Afectación parcial y temporal','Afectación significativa','Impacto serio o pérdida total'][x-1]}"
    )

    # Cálculos
    efec_norm = efectividad / 100
    amenaza_inherente = round(exposicion * probabilidad, 4)
    amenaza_residual = round(amenaza_inherente * (1 - efec_norm), 4)
    amenaza_residual_ajustada = round(amenaza_residual * amenaza_deliberada, 4)

    # Obtener ponderacion tipo impacto
    ponderacion = tabla_impacto.loc[tabla_impacto["Tipo"] == tipo_impacto, "Ponderacion"].values[0]

    impacto_valor_base = [5, 10, 30, 60, 85][impacto_nivel-1]
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
            "Tipo Impacto": tipo_impacto,
            "Exposición": exposicion,
            "Probabilidad": probabilidad,
            "Amenaza Deliberada": amenaza_deliberada,
            "Efectividad Control (%)": efectividad,
            "Impacto": impacto_nivel,
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
        fit_columns_on_grid_load=True,
        key="matriz_acumulativa"
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
