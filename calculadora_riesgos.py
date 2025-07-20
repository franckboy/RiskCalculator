import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

# Tabla oficial de tipo de impacto con normas y justificación
tabla_tipo_impacto = pd.DataFrame({
    "Código": ["H", "A", "E", "O", "I", "T", "R", "S", "C"],
    "Tipo de Impacto": [
        "Humano", "Ambiental", "Económico", "Operacional",
        "Infraestructura", "Tecnológico", "Reputacional",
        "Social", "Comercial"
    ],
    "Ponderación": [100, 85, 80, 75, 65, 60, 50, 45, 40],
    "Justificación": [
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

def mostrar_tabla_fija(df, titulo):
    st.markdown(f"### {titulo}")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True, filter=False, sortable=False)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, height=min(200, 35*len(df)), fit_columns_on_grid_load=True, enable_enterprise_modules=False, update_mode='NO_UPDATE')

def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto):
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

# Layout principal
col_izq, col_centro, col_der = st.columns([1.3, 2, 2])

with col_izq:
    mostrar_tabla_fija(tabla_efectividad[["Rango", "Mitigacion", "Descripcion"]], "Efectividad de Controles")
    mostrar_tabla_fija(tabla_exposicion[["Factor", "Nivel", "Descripcion"]], "Factor de Exposición")
    mostrar_tabla_fija(tabla_probabilidad[["Factor", "Nivel", "Descripcion"]], "Factor de Probabilidad")
    mostrar_tabla_fija(tabla_impacto[["Nivel", "Valor", "Descripcion"]], "Impacto / Severidad")
    mostrar_tabla_fija(tabla_tipo_impacto, "Tipo de Impacto y Justificación")
    st.markdown("### Índice de Criticidad")
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
    st.title("Calculadora de Riesgos")
    st.subheader("Datos del Riesgo")

    nombre_riesgo = st.text_input("Nombre del riesgo")
    descripcion = st.text_area("Descripción del riesgo")

    opciones_impacto_visibles = tabla_tipo_impacto.apply(
        lambda row: f"{row['Código']} - {row['Tipo de Impacto']}", axis=1).tolist()
    seleccion_impacto = st.selectbox("Tipo de Impacto", opciones_impacto_visibles)
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    justificacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Justificación"].values[0]
    ponderacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Ponderación"].values[0]
    st.markdown(f"**Justificación:** {justificacion_impacto}")

    exposicion = st.selectbox(
        "Factor de Exposición",
        options=tabla_exposicion["Factor"],
        format_func=lambda x: f"{x} - {tabla_exposicion.loc[tabla_exposicion['Factor']==x, 'Nivel'].values[0]}"
    )
    probabilidad = st.selectbox(
        "Factor de Probabilidad",
        options=tabla_probabilidad["Factor"],
        format_func=lambda x: f"{x} - {tabla_probabilidad.loc[tabla_probabilidad['Factor']==x, 'Nivel'].values[0]}"
    )
    amenaza_deliberada = st.selectbox(
        "Amenaza Deliberada",
        options=[1, 2, 3],
        format_func=lambda x: {1:"Baja", 2:"Intermedia", 3:"Alta"}[x],
        index=0
    )
    efectividad = st.slider("Efectividad del control (%)", 0, 100, 50)

    impacto = st.selectbox(
        "Impacto",
        options=tabla_impacto["Nivel"],
        format_func=lambda x: f"{x} - {tabla_impacto.loc[tabla_impacto['Nivel']==x, 'Descripcion'].values[0]}"
    )

    efectividad_norm = efectividad / 100
    valor_impacto = tabla_impacto.loc[tabla_impacto["Nivel"] == impacto, "Valor"].values[0]

    amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual = calcular_criticidad(
        probabilidad, exposicion, amenaza_deliberada, efectividad_norm, valor_impacto, ponderacion_impacto
    )

    clasificacion, color = clasificar_criticidad(riesgo_residual)

    st.markdown("### Resultados:")
    st.write(f"- Amenaza Inherente: {amenaza_inherente:.4f}")
    st.write(f"- Amenaza Residual: {amenaza_residual:.4f}")
    st.write(f"- Amenaza Residual Ajustada (x Amenaza Deliberada): {amenaza_residual_ajustada:.4f}")
    st.write(f"- Riesgo Residual: {riesgo_residual:.4f}")
    st.write(f"- Clasificación: **{clasificacion}** (Color: {color})")

    if st.button("Agregar riesgo a la matriz") and nombre_riesgo.strip() != "":
        nuevo_riesgo = {
            "Nombre Riesgo": nombre_riesgo.strip(),
            "Descripción": descripcion.strip(),
            "Tipo Impacto": codigo_impacto,
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
    st.header("Mapa de Calor por Tipo de Impacto y Probabilidad vs Impacto")

    if not st.session_state.riesgos.empty:
        # Valor para el mapa = Amenaza Residual Ajustada * Valor Impacto
        st.session_state.riesgos["Valor Mapa"] = (
            st.session_state.riesgos["Amenaza Residual Ajustada"] *
            st.session_state.riesgos["Impacto"].map(
                lambda x: tabla_impacto.loc[tabla_impacto["Nivel"] == x, "Valor"].values[0]
            )
        )

        matriz_calor = st.session_state.riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Probabilidad",
            values="Valor Mapa",
            aggfunc=np.mean
        ).fillna(0).sort_index()

        fig, ax = plt.subplots(figsize=(7,5))
        sns.heatmap(
            matriz_calor,
            annot=True,
            fmt=".2f",
            cmap=cmap,
            cbar_kws={"label": "Amenaza Residual Ajustada × Impacto"}
        )
        ax.set_xlabel("Probabilidad")
        ax.set_ylabel("Tipo de Impacto")
        st.pyplot(fig)
    else:
        st.info("Agrega riesgos para mostrar el mapa de calor.")

st.markdown("---")
st.header("Matriz Acumulativa de Riesgos")
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
    processed_data = output.getvalue()

    st.download_button(
        label="Descargar matriz de riesgos en Excel",
        data=processed_data,
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Agrega riesgos para mostrar la matriz acumulativa.")
