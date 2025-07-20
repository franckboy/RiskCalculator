import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap

st.set_page_config(layout="wide")

# --- Tablas fijas para referencia ---
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
    "Codigo": ["H","A","E","O","I","T","R","S","C"],
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

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Tipo Impacto",
        "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada", "Riesgo Residual",
        "Clasificación Criticidad", "Color Criticidad"
    ])

# --- Layout columnas ---
col_izq, col_centro, col_der = st.columns([1.2, 2, 1.5])

with col_izq:
    mostrar_tabla_fija(tabla_efectividad[["Rango", "Mitigacion", "Descripcion"]], "Efectividad de Controles")
    mostrar_tabla_fija(tabla_exposicion[["Factor", "Nivel", "Descripcion"]], "Factor de Exposición")
    mostrar_tabla_fija(tabla_probabilidad[["Factor", "Nivel", "Descripcion"]], "Factor de Probabilidad")
    mostrar_tabla_fija(tabla_impacto[["Codigo", "Tipo", "Ponderacion", "Justificacion"]], "Tipos de Impacto")

with col_centro:
    st.title("Calculadora de Riesgos")
    st.subheader("Datos del Riesgo")

    nombre_riesgo = st.text_input("Nombre del riesgo")
    descripcion = st.text_area("Descripción del riesgo")
    tipo_impacto = st.selectbox(
        "Tipo de Impacto",
        options=tabla_impacto["Tipo"],
        format_func=lambda x: f"{x} - {tabla_impacto.loc[tabla_impacto['Tipo']==x, 'Justificacion'].values[0]}"
    )
    exposicion = st.selectbox("Factor de Exposición", options=tabla_exposicion["Factor"], format_func=lambda x: f"{x} - {tabla_exposicion.loc[tabla_exposicion['Factor']==x, 'Nivel'].values[0]}")
    probabilidad = st.selectbox("Factor de Probabilidad", options=tabla_probabilidad["Factor"], format_func=lambda x: f"{x} - {tabla_probabilidad.loc[tabla_probabilidad['Factor']==x, 'Nivel'].values[0]}")
    amenaza_deliberada = st.selectbox("Amenaza Deliberada", options=[1,2,3], format_func=lambda x: {1:"Baja",2:"Intermedia",3:"Alta"}[x], index=0)
    efectividad = st.slider("Efectividad del control (%)", 0, 100, 50)
    impacto_nivel = st.selectbox("Impacto (nivel 1-5)", options=[1,2,3,4,5])
    
    # Cálculos
    efec_norm = efectividad / 100
    amenaza_inherente = round(exposicion * probabilidad, 4)
    amenaza_residual = round(amenaza_inherente * (1 - efec_norm), 4)
    amenaza_residual_ajustada = round(amenaza_residual * amenaza_deliberada, 4)
    
    valor_impacto = impacto_nivel * tabla_impacto.loc[tabla_impacto["Tipo"] == tipo_impacto, "Ponderacion"].values[0] / 100
    
    riesgo_residual = round(amenaza_residual_ajustada * valor_impacto, 4)
    clasificacion, color = clasificar_criticidad(riesgo_residual)
    
    st.markdown("### Resultados:")
    st.write(f"- Amenaza Inherente: {amenaza_inherente}")
    st.write(f"- Amenaza Residual: {amenaza_residual}")
    st.write(f"- Amenaza Residual Ajustada (x Amenaza Deliberada): {amenaza_residual_ajustada}")
    st.write(f"- Valor Impacto Ajustado: {valor_impacto:.4f}")
    st.write(f"- Riesgo Residual: {riesgo_residual}")
    st.markdown(f"- Clasificación: **{clasificacion}**", unsafe_allow_html=True)
    st.markdown(f"<span style='color:{color}; font-weight:bold;'>■</span>", unsafe_allow_html=True)
    
    if st.button("Agregar riesgo a la matriz") and nombre_riesgo.strip() != "":
        nuevo_riesgo = {
            "Nombre Riesgo": nombre_riesgo.strip(),
            "Descripción": descripcion.strip(),
            "Exposición": exposicion,
            "Probabilidad": probabilidad,
            "Amenaza Deliberada": amenaza_deliberada,
            "Efectividad Control (%)": efectividad,
            "Impacto": impacto_nivel,
            "Tipo Impacto": tipo_impacto,
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
    st.header("Mapa de Calor y Gráficos")
    if not st.session_state.riesgos.empty:
        # Preparar datos
        st.session_state.riesgos["Impacto Ajustado"] = st.session_state.riesgos["Impacto"] * st.session_state.riesgos["Tipo Impacto"].map(
            dict(zip(tabla_impacto["Tipo"], tabla_impacto["Ponderacion"])))/100
        
        # Mapa de calor: probabilidad vs impacto ajustado (usando Riesgo residual)
        matriz_calor = st.session_state.riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Probabilidad",
            values="Riesgo Residual",
            aggfunc=np.mean
        ).fillna(0).sort_index()

        fig, ax = plt.subplots(figsize=(7,5))
        sns.heatmap(
            matriz_calor,
            annot=True,
            fmt=".2f",
            cmap=cmap,
            cbar_kws={"label": "Riesgo Residual"}
        )
        ax.set_xlabel("Probabilidad")
        ax.set_ylabel("Tipo de Impacto")
        ax.set_title("Mapa de Calor: Riesgo Residual por Tipo Impacto y Probabilidad")
        st.pyplot(fig)

        # Diagrama de Pareto - Prioridad riesgos
        st.subheader("Diagrama de Pareto")
        pareto_df = st.session_state.riesgos.groupby("Tipo Impacto")["Riesgo Residual"].sum().reset_index()
        pareto_df = pareto_df.sort_values(by="Riesgo Residual", ascending=False)
        pareto_df["Acumulado"] = pareto_df["Riesgo Residual"].cumsum()

        fig2, ax2 = plt.subplots()
        ax2.bar(pareto_df["Tipo Impacto"], pareto_df["Riesgo Residual"], color="skyblue")
        ax2.plot(pareto_df["Tipo Impacto"], pareto_df["Acumulado"], color="red", marker="o")
        ax2.set_ylabel("Suma Riesgo Residual")
        ax2.set_title("Diagrama de Pareto - Riesgos por Tipo de Impacto")
        st.pyplot(fig2)

    else:
        st.info("Agrega riesgos para mostrar mapa de calor y gráficos.")

# Matriz acumulativa abajo (full width)
st.markdown("---")
st.subheader("Matriz Acumulativa de Riesgos")
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

    # Exportar Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        st.session_state.riesgos.to_excel(writer, index=False, sheet_name="Riesgos")
        writer.save()
    processed_data = output.getvalue()

    st.download_button(
        label="Descargar matriz de riesgos en Excel",
        data=processed_data,
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Agrega riesgos para mostrar la matriz acumulativa.")
