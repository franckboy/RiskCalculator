import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from st_aggrid import AgGrid, GridOptionsBuilder
from io import BytesIO

st.set_page_config(page_title="Evaluación de Riesgos", layout="wide")

# ---------- Datos base: tablas fijas ----------
def cargar_tablas_fijas():
    controles = pd.DataFrame({
        "Clasificación": ["Alta", "Media", "Baja", "Ineficaz"],
        "Valor": [0.1, 0.3, 0.6, 1.0]
    })

    exposicion = pd.DataFrame({
        "Descripción": ["Constante", "Frecuente", "Ocasional", "Rara vez"],
        "Valor": [1.0, 0.75, 0.5, 0.25]
    })

    probabilidad = pd.DataFrame({
        "Descripción": ["Muy alta", "Alta", "Media", "Baja"],
        "Valor": [1.0, 0.75, 0.5, 0.25]
    })

    impacto = pd.DataFrame({
        "Descripción": ["Catastrófico", "Crítico", "Moderado", "Menor"],
        "Valor": [1.0, 0.75, 0.5, 0.25]
    })

    return controles, exposicion, probabilidad, impacto

controles, exposicion, probabilidad, impacto = cargar_tablas_fijas()

# ---------- Sidebar: entrada de riesgo ----------
st.sidebar.title("Ingreso de Riesgo")
riesgo = st.sidebar.text_input("Nombre del riesgo")
impacto_val = st.sidebar.selectbox("Impacto (afectación)", impacto["Valor"], format_func=lambda x: impacto[impacto["Valor"]==x]["Descripción"].values[0])
probabilidad_base = st.sidebar.selectbox("Probabilidad (tras controles)", probabilidad["Valor"], format_func=lambda x: probabilidad[probabilidad["Valor"]==x]["Descripción"].values[0])
exposicion_val = st.sidebar.selectbox("Factor de exposición", exposicion["Valor"], format_func=lambda x: exposicion[exposicion["Valor"]==x]["Descripción"].values[0])
control_val = st.sidebar.selectbox("Efectividad de controles", controles["Valor"], format_func=lambda x: controles[controles["Valor"]==x]["Clasificación"].values[0])
amenaza_deliberada = st.sidebar.slider("Amenaza deliberada (1 = baja, 3 = alta intención)", 1, 3, 1)

# ---------- Cálculo de criticidad ----------
if riesgo:
    # Ajustar probabilidad
    prob_ajustada = probabilidad_base * control_val * exposicion_val * amenaza_deliberada

    # Cálculo del índice de criticidad
    criticidad = impacto_val * prob_ajustada

    st.markdown(f"### Riesgo: `{riesgo}`")
    st.metric("Índice de criticidad", f"{criticidad:.3f}")

    # ---------- Guardar en lista acumulativa ----------
    if "datos_riesgo" not in st.session_state:
        st.session_state.datos_riesgo = []

    if st.sidebar.button("Guardar riesgo"):
        st.session_state.datos_riesgo.append({
            "Riesgo": riesgo,
            "Impacto": impacto_val,
            "Probabilidad ajustada": prob_ajustada,
            "Criticidad": criticidad
        })

# ---------- Mostrar matriz acumulativa ----------
if st.session_state.get("datos_riesgo"):
    st.markdown("## Matriz acumulativa de riesgos")
    df = pd.DataFrame(st.session_state.datos_riesgo)

    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(editable=False, filter=False, sortable=True)
    grid_options = gb.build()

    AgGrid(df, gridOptions=grid_options, height=300, theme="streamlit")

    # ---------- Mapa de calor ----------
    st.markdown("## Mapa de calor (Probabilidad vs Impacto)")

    heatmap = pd.pivot_table(
        df,
        index="Probabilidad ajustada",
        columns="Impacto",
        values="Criticidad",
        aggfunc="sum",
        fill_value=0
    )

    st.dataframe(heatmap.style.background_gradient(cmap="YlOrRd"), height=300)

    # ---------- Diagrama de Pareto ----------
    st.markdown("## Diagrama de Pareto de Criticidad")

    df_pareto = df.sort_values(by="Criticidad", ascending=False).copy()
    df_pareto["Acumulado"] = df_pareto["Criticidad"].cumsum()
    df_pareto["% Acumulado"] = 100 * df_pareto["Acumulado"] / df_pareto["Criticidad"].sum()

    fig = go.Figure()

    # Barras de criticidad
    fig.add_trace(go.Bar(
        x=df_pareto["Riesgo"],
        y=df_pareto["Criticidad"],
        name="Criticidad",
        marker_color='indianred'
    ))

    # Línea acumulada
    fig.add_trace(go.Scatter(
        x=df_pareto["Riesgo"],
        y=df_pareto["% Acumulado"],
        name="% Acumulado",
        yaxis='y2',
        mode='lines+markers',
        marker_color='blue'
    ))

    fig.update_layout(
        title="Pareto de Riesgos",
        xaxis=dict(title="Riesgo"),
        yaxis=dict(title="Criticidad"),
        yaxis2=dict(title="% Acumulado", overlaying='y', side='right', range=[0, 110]),
        legend=dict(x=0.8, y=1.2)
    )

    st.plotly_chart(fig, use_container_width=True)

    # ---------- Exportar a Excel ----------
    st.markdown("## Exportar resultados")
    def exportar_excel(df_export):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Riesgos')
        return output.getvalue()

    excel_data = exportar_excel(df)

    st.download_button(
        label="📥 Descargar Excel",
        data=excel_data,
        file_name="evaluacion_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------- Mostrar tablas fijas sin scroll ni filtros ----------
st.markdown("## Tablas fijas de referencia")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**Efectividad de controles**")
    st.dataframe(controles, use_container_width=True, hide_index=True)
with col2:
    st.markdown("**Factor de exposición**")
    st.dataframe(exposicion, use_container_width=True, hide_index=True)
with col3:
    st.markdown("**Factor de probabilidad**")
    st.dataframe(probabilidad, use_container_width=True, hide_index=True)

st.markdown("**Impacto o severidad**")
st.dataframe(impacto, use_container_width=True, hide_index=True)

