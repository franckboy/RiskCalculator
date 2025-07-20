import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder
import plotly.express as px
from io import BytesIO

# --- Datos fijos actualizados ---
tablas = {
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
        "Color": ["green", "gold", "orange", "red"]
    }),
    "semaforo": pd.DataFrame({
        "Color": ["Verde", "Amarillo", "Naranja", "Rojo"],
        "Significado": ["Aceptable", "Tolerable", "Inaceptable", "Inadmisible"]
    }),
}

# --- Traducciones ---
labels_es = {
    "titulo": "🛡️ Calculadora de Riesgos ASIS",
    "idioma_label": "Selecciona idioma",
    "nombre": "Nombre del riesgo",
    "descripcion": "Descripción del riesgo",
    "exposicion": "Factor de Exposición",
    "probabilidad": "Factor de Probabilidad",
    "efectividad": "Efectividad del control (%)",
    "impacto": "Impacto (1 a 5)",
    "amenaza_deliberada": "Amenaza Deliberada (1 a 3)",
    "tipo_impacto": "Tipo de Impacto",
    "agregar": "Agregar riesgo a la matriz",
    "matriz_acum": "Matriz acumulativa de riesgos",
    "mapa_calor": "Mapa de calor (Probabilidad × Impacto)",
    "grafico_tipo": "Número de riesgos por Impacto",
    "grafico_dist": "Distribución de Riesgo Residual",
    "descargar_excel": "📥 Descargar matriz de riesgos en Excel",
}

labels_en = {
    "titulo": "🛡️ ASIS Risk Calculator",
    "idioma_label": "Select language",
    "nombre": "Risk name",
    "descripcion": "Risk description",
    "exposicion": "Exposure Factor",
    "probabilidad": "Probability Factor",
    "efectividad": "Control Effectiveness (%)",
    "impacto": "Impact (1 to 5)",
    "amenaza_deliberada": "Deliberate Threat (1 to 3)",
    "tipo_impacto": "Impact Type",
    "agregar": "Add risk to matrix",
    "matriz_acum": "Cumulative Risk Matrix",
    "mapa_calor": "Heatmap (Probability × Impact)",
    "grafico_tipo": "Number of risks by Impact",
    "grafico_dist": "Residual Risk Distribution",
    "descargar_excel": "📥 Download risk matrix as Excel",
}

def clasificar_criticidad(valor, tabla_criticidad):
    for i, row in tabla_criticidad.iterrows():
        if valor <= row["Límite Superior"]:
            return row["Clasificación"], row["Color"]
    return "Desconocido", "black"

def riesgo_residual_calc(valor_efectividad, expo, prob, amenaza_delib, valor_impacto):
    # Ajusta probabilidad con amenaza deliberada
    prob_ajustada = min(prob * amenaza_delib, 1.0)
    amenaza_inherente = expo * prob_ajustada
    amenaza_residual = amenaza_inherente * (1 - valor_efectividad)
    riesgo_residual = amenaza_residual * valor_impacto
    return riesgo_residual

def descargar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Riesgos")
    return output.getvalue()

def mostrar_tabla_aggrid_centrada(df, titulo):
    st.markdown(f"**{titulo}**")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=False, filter=False, sortable=False, resizable=True,
                                cellStyle={"textAlign": "center", "verticalAlign": "middle"})
    gb.configure_grid_options(domLayout='autoHeight')
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, fit_columns_on_grid_load=True, height=df.shape[0]*35 + 30)

def main():
    st.set_page_config(layout="wide")

    # Selector idioma arriba y global labels
    idioma = st.selectbox(
        "Selecciona idioma / Select language",
        options=["Español", "English"],
        index=0,
        help="Elige el idioma para la aplicación / Choose app language"
    )
    labels = labels_es if idioma == "Español" else labels_en

    # Título
    st.title(labels["titulo"])

    if "riesgos" not in st.session_state:
        st.session_state.riesgos = pd.DataFrame(columns=[
            "Nombre Riesgo", "Descripción", "Efectividad Control", "Valor Efectividad",
            "Exposición", "Valor Exposición", "Probabilidad", "Valor Probabilidad",
            "Amenaza Deliberada", "Impacto", "Valor Impacto", "Riesgo Residual", "Tipo Impacto"
        ])

    col1, col2, col3 = st.columns([1.2, 2.0, 1.8])

    # IZQUIERDA - Tablas fijas
    with col1:
        mostrar_tabla_aggrid_centrada(tablas["efectividad"], labels["efectividad"])
        mostrar_tabla_aggrid_centrada(tablas["exposicion"], labels["exposicion"])
        mostrar_tabla_aggrid_centrada(tablas["probabilidad"], labels["probabilidad"])
        mostrar_tabla_aggrid_centrada(tablas["impacto"], labels["impacto"])
        mostrar_tabla_aggrid_centrada(tablas["criticidad"].drop(columns=["Color"]), "Índice de Criticidad")
        mostrar_tabla_aggrid_centrada(tablas["semaforo"], "Semáforo / Legend")

    # CENTRO - Formulario y matriz acumulativa
    with col2:
        st.subheader(labels["nombre"])
        nombre = st.text_input(labels["nombre"])
        st.subheader(labels["descripcion"])
        descripcion = st.text_area(labels["descripcion"], height=70)

        exposicion = st.selectbox(labels["exposicion"], tablas["exposicion"]["Factor"])
        probabilidad = st.selectbox(labels["probabilidad"], tablas["probabilidad"]["Factor"])
        efectividad = st.slider(labels["efectividad"], 0, 100, 50)
        amenaza_deliberada = st.select_slider(
            labels["amenaza_deliberada"], options=[1, 2, 3], value=1,
            help="Un valor mayor aumenta la probabilidad por amenaza deliberada"
        )
        impacto = st.selectbox(
            labels["impacto"],
            tablas["impacto"]["Nivel"],
            format_func=lambda x: f"{x} - {tablas['impacto'].loc[tablas['impacto']['Nivel']==x, 'Clasificacion'].values[0]}"
        )
        tipo_impacto = st.selectbox(
            labels["tipo_impacto"],
            ["Humano", "Económico", "Operacional", "Ambiental", "Infraestructura", "Tecnológico", "Reputacional", "Comercial", "Social"]
        )

        valor_efec = efectividad / 100
        nivel_expo = exposicion
        nivel_prob = probabilidad
        valor_impacto = tablas["impacto"].loc[tablas["impacto"]["Nivel"] == impacto, "Valor"].values[0]

        riesgo_res = riesgo_residual_calc(valor_efec, nivel_expo, nivel_prob, amenaza_deliberada, valor_impacto)

        st.markdown("### Resultados del nuevo riesgo:")
        st.write(f"- Amenaza Inherente ajustada (Exposición × Probabilidad × Amenaza Deliberada): "
                 f"{round(nivel_expo * min(nivel_prob * amenaza_deliberada, 1.0),4)}")
        st.write(f"- Riesgo Residual: {round(riesgo_res, 4)}")

        if st.button(labels["agregar"]) and nombre.strip() != "":
            nuevo = {
                "Nombre Riesgo": nombre.strip(),
                "Descripción": descripcion.strip(),
                "Efectividad Control": efectividad,
                "Valor Efectividad": valor_efec,
                "Exposición": nivel_expo,
                "Valor Exposición": nivel_expo,
                "Probabilidad": nivel_prob,
                "Valor Probabilidad": nivel_prob,
                "Amenaza Deliberada": amenaza_deliberada,
                "Impacto": impacto,
                "Valor Impacto": valor_impacto,
                "Riesgo Residual": riesgo_res,
                "Tipo Impacto": tipo_impacto
            }
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo])], ignore_index=True)
            st.success("Riesgo agregado.")

        # Impacto acumulado e índice global
        impacto_acum = st.session_state.riesgos["Riesgo Residual"].sum()
        indice_criticidad = impacto_acum / 294 * 100  # Norma ASIS

        clasif, color = clasificar_criticidad(indice_criticidad, tablas["criticidad"])
        st.markdown(f"**Impacto acumulado:** {impacto_acum:.2f}")
        st.markdown(f"**Índice de criticidad global:** "
                    f"<span style='color:{color}; font-weight:bold'>{indice_criticidad:.2f} ({clasif})</span>", unsafe_allow_html=True)

        # Matriz acumulativa (abajo del formulario)
        st.header(labels["matriz_acum"])
        if not st.session_state.riesgos.empty:
            gb = GridOptionsBuilder.from_dataframe(st.session_state.riesgos)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_default_column(editable=False, filter=True, sortable=True, resizable=True)
            gridOptions = gb.build()
            AgGrid(st.session_state.riesgos, gridOptions=gridOptions, height=300, fit_columns_on_grid_load=True)
        else:
            st.info("Agrega riesgos para ver la matriz.")

    # DERECHA - Mapas de calor y gráficos
    with col3:
        st.header(labels["mapa_calor"])
        if not st.session_state.riesgos.empty:
            df_heatmap = st.session_state.riesgos.copy()
            df_heatmap["Prob_Impacto"] = df_heatmap["Valor Probabilidad"] * df_heatmap["Valor Impacto"]

            fig_heat = px.density_heatmap(
                df_heatmap,
                x="Probabilidad",
                y="Impacto",
                z="Prob_Impacto",
                nbinsx=5,
                nbinsy=5,
                color_continuous_scale=["green", "yellow", "orange", "red"],
                labels={"Probabilidad": labels["probabilidad"], "Impacto": labels["impacto"], "Prob_Impacto": "Prob × Impacto"}
            )
            fig_heat.update_layout(coloraxis_colorbar=dict(title="Riesgo Residual"))
            st.plotly_chart(fig_heat, use_container_width=True)

            st.subheader(labels["grafico_tipo"])
            chart_data = st.session_state.riesgos["Impacto"].value_counts().reset_index()
            chart_data.columns = ["Impacto", "Cantidad"]
            fig_bar = px.bar(chart_data, x="Impacto", y="Cantidad", color="Impacto", labels={"Cantidad": "Número de riesgos"})
            st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader(labels["grafico_dist"])
            fig_hist = px.histogram(st.session_state.riesgos, x="Riesgo Residual", nbins=20,
                                    labels={"Riesgo Residual": "Riesgo Residual"})
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Agrega riesgos para ver los gráficos.")

        # Botón para descargar Excel (aquí también por comodidad)
        if not st.session_state.riesgos.empty:
            excel_data = descargar_excel(st.session_state.riesgos)
            st.download_button(labels["descargar_excel"], data=excel_data, file_name="matriz_riesgos_asis.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
