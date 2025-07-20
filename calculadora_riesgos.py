import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
import io

# --- Datos estáticos fijos, traducibles ---
def tablas_fijas(idioma="es"):
    if idioma == "es":
        return {
            "exposicion": pd.DataFrame({
                "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
                "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
                "Definición de Criterios": [
                    "Exposición extremadamente rara",
                    "Exposición ocasional (cada 10 años)",
                    "Exposición algunas veces al año",
                    "Exposición mensual",
                    "Exposición frecuente o semanal"
                ]
            }),
            "probabilidad": pd.DataFrame({
                "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
                "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
                "Descripcion": [
                    "En condiciones excepcionales",
                    "Ha sucedido alguna vez",
                    "Podría ocurrir ocasionalmente",
                    "Probable en ocasiones",
                    "Ocurre con frecuencia / inminente"
                ]
            }),
            "efectividad": pd.DataFrame({
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
            }),
            "impacto": pd.DataFrame({
                "Nivel": [1, 2, 3, 4, 5],
                "Valor": [5, 10, 30, 60, 85],
                "Clasificacion": ["Insignificante", "Leve", "Moderado", "Grave", "Critico"],
                "Definición de Criterios": [
                    "No afecta significativamente",
                    "Afectación menor",
                    "Afectación parcial y temporal",
                    "Afectación significativa",
                    "Impacto serio o pérdida total"
                ]
            }),
            "criticidad": pd.DataFrame({
                "Límite Superior": [2, 4, 15, float('inf')],
                "Clasificación": ["ACEPTABLE", "TOLERABLE", "INACEPTABLE", "INADMISIBLE"],
                "Rango Aceptabilidad": ["≤ 2", "≤ 4", "≤ 15", "> 15"],
                "Color": ["#008000", "#FFD700", "#FFA500", "#FF0000"]
            }),
            "semaforo": pd.DataFrame({
                "Nivel": ["Bajo", "Medio", "Alto", "Extremo"],
                "Color": ["🟩", "🟨", "🟧", "🟥"]
            }),
            "labels": {
                "nombre": "Nombre del riesgo",
                "descripcion": "Descripción del riesgo",
                "efectividad": "Efectividad del control",
                "exposicion": "Factor de Exposición",
                "probabilidad": "Factor de Probabilidad",
                "amenaza_delib": "Amenaza deliberada (1=baja, 3=alta)",
                "impacto": "Impacto / Severidad",
                "agregar": "Agregar riesgo",
                "matriz_acum": "Matriz Acumulativa de Riesgos",
                "indice_criticidad": "Índice global de criticidad ASIS",
                "impacto_acumulado": "Impacto acumulado",
                "mapa_calor": "Mapa de calor (Probabilidad × Impacto)",
                "grafico_tipo": "Gráfico de Riesgos por Tipo de Impacto",
                "grafico_dist": "Distribución del Riesgo Residual"
            }
        }
    else:
        # Traducciones en inglés (puedes completar o modificar)
        return {
            "exposicion": pd.DataFrame({
                "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
                "Nivel": ["Very Low", "Low", "Moderate", "High", "Very High"],
                "Definición de Criterios": [
                    "Extremely rare exposure",
                    "Occasional exposure (every 10 years)",
                    "Exposure several times per year",
                    "Monthly exposure",
                    "Frequent or weekly exposure"
                ]
            }),
            "probabilidad": pd.DataFrame({
                "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
                "Nivel": ["Very Low", "Low", "Moderate", "High", "Very High"],
                "Descripcion": [
                    "Under exceptional conditions",
                    "Has happened once",
                    "Could happen occasionally",
                    "Likely sometimes",
                    "Happens frequently/imminent"
                ]
            }),
            "efectividad": pd.DataFrame({
                "Rango": ["0%", "1 - 20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
                "Factor": [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.1],
                "Mitigacion": ["Ineffective", "Limited", "Low", "Intermediate", "High", "Very High", "Total"],
                "Descripcion": [
                    "Does not reduce risk",
                    "Reduces only under ideal conditions",
                    "Mitigates minor risks.",
                    "Standard control with limitations.",
                    "Significantly reduces risk",
                    "Robust and well-implemented control.",
                    "Eliminates almost all risk"
                ]
            }),
            "impacto": pd.DataFrame({
                "Nivel": [1, 2, 3, 4, 5],
                "Valor": [5, 10, 30, 60, 85],
                "Clasificacion": ["Insignificant", "Minor", "Moderate", "Severe", "Critical"],
                "Definición de Criterios": [
                    "Does not significantly affect",
                    "Minor affectation",
                    "Partial and temporary affectation",
                    "Significant affectation",
                    "Serious impact or total loss"
                ]
            }),
            "criticidad": pd.DataFrame({
                "Límite Superior": [2, 4, 15, float('inf')],
                "Clasificación": ["ACCEPTABLE", "TOLERABLE", "UNACCEPTABLE", "UNADMISSIBLE"],
                "Rango Aceptabilidad": ["≤ 2", "≤ 4", "≤ 15", "> 15"],
                "Color": ["#008000", "#FFD700", "#FFA500", "#FF0000"]
            }),
            "semaforo": pd.DataFrame({
                "Nivel": ["Low", "Medium", "High", "Extreme"],
                "Color": ["🟩", "🟨", "🟧", "🟥"]
            }),
            "labels": {
                "nombre": "Risk name",
                "descripcion": "Risk description",
                "efectividad": "Control effectiveness",
                "exposicion": "Exposure factor",
                "probabilidad": "Probability factor",
                "amenaza_delib": "Deliberate threat (1=low, 3=high)",
                "impacto": "Impact / Severity",
                "agregar": "Add risk",
                "matriz_acum": "Cumulative Risk Matrix",
                "indice_criticidad": "Global ASIS Criticality Index",
                "impacto_acumulado": "Accumulated Impact",
                "mapa_calor": "Heatmap (Probability × Impact)",
                "grafico_tipo": "Risk Chart by Impact Type",
                "grafico_dist": "Residual Risk Distribution"
            }
        }

# --- Funciones para lógica ---
def clasificar_criticidad(valor, tabla_criticidad):
    for _, row in tabla_criticidad.iterrows():
        if valor <= row["Límite Superior"]:
            return row["Clasificación"], row["Color"]
    return "No clasificado", "#000000"

def riesgo_residual_calc(efectividad, exposicion, probabilidad, amenaza_delib, impacto):
    # efec, expo, prob son factores (0-1), amenaza_delib es 1-3, impacto es valor numérico
    return round((1 - efectividad) * exposicion * probabilidad * amenaza_delib * impacto, 4)

def descargar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Riesgos")
    return output.getvalue()

# --- INTERFAZ ---
def main():
    st.set_page_config(layout="wide", page_title="Calculadora de Riesgos ASIS")

    # Selector de idioma
    idioma = st.sidebar.selectbox("Idioma / Language", options=["Español", "English"])
    lang = "es" if idioma == "Español" else "en"

    tablas = tablas_fijas(lang)
    labels = tablas["labels"]

    # Inicializar estado
    if "riesgos" not in st.session_state:
        st.session_state.riesgos = pd.DataFrame(columns=[
            "Nombre Riesgo", "Descripción", "Efectividad Control", "Valor Efectividad",
            "Exposición", "Valor Exposición", "Probabilidad", "Valor Probabilidad",
            "Amenaza Deliberada", "Impacto", "Valor Impacto",
            "Riesgo Residual"
        ])

    # Layout columnas
    col1, col2, col3 = st.columns([1.2, 2.0, 1.8])

    with col1:
        st.markdown("### Tablas fijas")
        mostrar_tabla_aggrid(tablas["efectividad"], labels["efectividad"])
        mostrar_tabla_aggrid(tablas["exposicion"], labels["exposicion"])
        mostrar_tabla_aggrid(tablas["probabilidad"], labels["probabilidad"])
        mostrar_tabla_aggrid(tablas["impacto"], labels["impacto"])
        mostrar_tabla_aggrid(tablas["criticidad"].drop(columns=["Color"]), labels["indice_criticidad"])
        mostrar_tabla_aggrid(tablas["semaforo"], "Semáforo / Legend")

    with col2:
        st.title("🛡️ Calculadora de Riesgos ASIS")
        st.subheader("Ingresar nuevo riesgo")

        nombre = st.text_input(labels["nombre"])
        descripcion = st.text_area(labels["descripcion"], help="Descripción breve del riesgo")

        efec = st.selectbox(
            labels["efectividad"],
            options=tablas["efectividad"]["Rango"],
            help="Seleccione el nivel de efectividad del control"
        )
        valor_efec = tablas["efectividad"].loc[tablas["efectividad"]["Rango"] == efec, "Factor"].values[0]

        expo = st.selectbox(
            labels["exposicion"],
            options=tablas["exposicion"]["Factor"],
            format_func=lambda x: f"{x} - {tablas['exposicion'].loc[tablas['exposicion']['Factor']==x,'Nivel'].values[0]}",
            help="Seleccione el factor de exposición"
        )
        nivel_expo = tablas["exposicion"].loc[tablas["exposicion"]["Factor"] == expo, "Nivel"].values[0]

        prob = st.selectbox(
            labels["probabilidad"],
            options=tablas["probabilidad"]["Factor"],
            format_func=lambda x: f"{x} - {tablas['probabilidad'].loc[tablas['probabilidad']['Factor']==x,'Nivel'].values[0]}",
            help="Seleccione el factor de probabilidad"
        )
        nivel_prob = tablas["probabilidad"].loc[tablas["probabilidad"]["Factor"] == prob, "Nivel"].values[0]

        amenaza_delib = st.select_slider(
            labels["amenaza_delib"],
            options=[1, 2, 3],
            value=1,
            help="1 = baja intención, 3 = alta intención"
        )

        impact = st.selectbox(
            labels["impacto"],
            options=tablas["impacto"]["Nivel"],
            format_func=lambda x: f"{x} - {tablas['impacto'].loc[tablas['impacto']['Nivel']==x, 'Clasificacion'].values[0]}",
            help="Seleccione el nivel de impacto"
        )
        valor_impacto = tablas["impacto"].loc[tablas["impacto"]["Nivel"] == impact, "Valor"].values[0]

        if st.button(labels["agregar"]):
            if not nombre.strip():
                st.error("Debe ingresar un nombre para el riesgo.")
            elif not descripcion.strip():
                st.error("Debe ingresar una descripción para el riesgo.")
            else:
                riesgo_res = riesgo_residual_calc(
                    valor_efec, expo, prob, amenaza_delib, valor_impacto
                )

                # Guardar riesgo
                nuevo = {
                    "Nombre Riesgo": nombre.strip(),
                    "Descripción": descripcion.strip(),
                    "Efectividad Control": efec,
                    "Valor Efectividad": valor_efec,
                    "Exposición": nivel_expo,
                    "Valor Exposición": expo,
                    "Probabilidad": nivel_prob,
                    "Valor Probabilidad": prob,
                    "Amenaza Deliberada": amenaza_delib,
                    "Impacto": impact,
                    "Valor Impacto": valor_impacto,
                    "Riesgo Residual": riesgo_res
                }
                st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo])], ignore_index=True)
                st.success("Riesgo agregado.")

        # Mostrar impacto acumulado y crítico global
        impacto_acum = st.session_state.riesgos["Riesgo Residual"].sum()
        indice_criticidad = impacto_acum / 294 * 100  # según ASIS

        clasif, color = clasificar_criticidad(indice_criticidad, tablas["criticidad"])
        st.markdown(f"**Impacto acumulado:** {impacto_acum:.2f}")
        st.markdown(f"**Índice de criticidad global:** <span style='color:{color};font-weight:bold'>{indice_criticidad:.2f} ({clasif})</span>", unsafe_allow_html=True)

        # Botón para descargar excel
        if not st.session_state.riesgos.empty:
            excel_data = descargar_excel(st.session_state.riesgos)
            st.download_button("📥 Descargar matriz de riesgos en Excel", data=excel_data, file_name="matriz_riesgos_asis.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with col3:
        st.header(labels["matriz_acum"])

        if not st.session_state.riesgos.empty:
            # Tabla ordenable con AgGrid
            gb = GridOptionsBuilder.from_dataframe(st.session_state.riesgos)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_default_column(editable=False, filter=True, sortable=True)
            gridOptions = gb.build()
            AgGrid(st.session_state.riesgos, gridOptions=gridOptions, height=300, fit_columns_on_grid_load=True)

            # Mapa de calor interactivo Plotly (Probabilidad * Impacto)
            st.subheader(labels["mapa_calor"])
            df_heatmap = st.session_state.riesgos.copy()
            df_heatmap["Prob_Impacto"] = df_heatmap["Valor Probabilidad"] * df_heatmap["Valor Impacto"]

            heatmap_fig = px.density_heatmap(
                df_heatmap,
                x="Probabilidad",
                y="Impacto",
                z="Prob_Impacto",
                nbinsx=5,
                nbinsy=5,
                color_continuous_scale=["green", "yellow", "orange", "red"],
                labels={"Probabilidad": labels["probabilidad"], "Impacto": labels["impacto"], "Prob_Impacto": "Prob × Impacto"}
            )
            heatmap_fig.update_layout(coloraxis_colorbar=dict(title="Riesgo Residual"))
            st.plotly_chart(heatmap_fig, use_container_width=True)

            # Gráfico barras: número de riesgos por tipo impacto
            st.subheader(labels["grafico_tipo"])
            chart_data = st.session_state.riesgos["Impacto"].value_counts().reset_index()
            chart_data.columns = ["Impacto", "Cantidad"]
            bar_fig = px.bar(chart_data, x="Impacto", y="Cantidad", color="Impacto", labels={"Cantidad": "Número de riesgos"})
            st.plotly_chart(bar_fig, use_container_width=True)

            # Gráfico distribución Riesgo Residual
            st.subheader(labels["grafico_dist"])
            hist_fig = px.histogram(st.session_state.riesgos, x="Riesgo Residual", nbins=20, labels={"Riesgo Residual": "Riesgo Residual"})
            st.plotly_chart(hist_fig, use_container_width=True)
        else:
            st.info("Agrega riesgos para ver la matriz y gráficos.")

def mostrar_tabla_aggrid(df, titulo):
    st.markdown(f"**{titulo}**")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=False, filter=False, sortable=False, resizable=True)
    gb.configure_grid_options(domLayout='autoHeight')
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, fit_columns_on_grid_load=True, height=df.shape[0]*35 + 30)

if __name__ == "__main__":
    main()
