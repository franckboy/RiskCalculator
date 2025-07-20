import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

# Traducciones para el selector de idioma
idiomas = {
    "es": {
        "titulo": "Calculadora de Riesgos",
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion_riesgo": "Descripción del riesgo",
        "tipo_impacto": "Tipo de Impacto",
        "factor_exposicion": "Factor de Exposición",
        "factor_probabilidad": "Factor de Probabilidad",
        "amenaza_deliberada": "Amenaza Deliberada",
        "efectividad_control": "Efectividad del control (%)",
        "impacto": "Impacto",
        "agregar_riesgo": "Agregar riesgo a la matriz",
        "resultado": "Resultados",
        "amenaza_inherente": "Amenaza Inherente",
        "amenaza_residual": "Amenaza Residual",
        "amenaza_residual_ajustada": "Amenaza Residual Ajustada (x Amenaza Deliberada)",
        "riesgo_residual": "Riesgo Residual",
        "clasificacion": "Clasificación",
        "color": "Color",
        "mapa_calor": "Mapa de Calor por Tipo de Impacto y Probabilidad x Impacto",
        "matriz_acumulativa": "Matriz Acumulativa de Riesgos",
        "descargar_excel": "Descargar matriz de riesgos en Excel",
        "tablas_fijas": "Tablas de Referencia",
        "efectividad_controles": "Efectividad de Controles",
        "factor_exposicion_tabla": "Factor de Exposición",
        "factor_probabilidad_tabla": "Factor de Probabilidad",
        "impacto_tabla": "Impacto / Severidad",
        "indice_criticidad": "Índice de Criticidad",
    },
    "en": {
        "titulo": "Risk Calculator",
        "nombre_riesgo": "Risk Name",
        "descripcion_riesgo": "Risk Description",
        "tipo_impacto": "Impact Type",
        "factor_exposicion": "Exposure Factor",
        "factor_probabilidad": "Probability Factor",
        "amenaza_deliberada": "Deliberate Threat",
        "efectividad_control": "Control Effectiveness (%)",
        "impacto": "Impact",
        "agregar_riesgo": "Add Risk to Matrix",
        "resultado": "Results",
        "amenaza_inherente": "Inherent Threat",
        "amenaza_residual": "Residual Threat",
        "amenaza_residual_ajustada": "Adjusted Residual Threat (x Deliberate Threat)",
        "riesgo_residual": "Residual Risk",
        "clasificacion": "Classification",
        "color": "Color",
        "mapa_calor": "Heatmap by Impact Type and Probability x Impact",
        "matriz_acumulativa": "Cumulative Risk Matrix",
        "descargar_excel": "Download Risk Matrix in Excel",
        "tablas_fijas": "Reference Tables",
        "efectividad_controles": "Control Effectiveness",
        "factor_exposicion_tabla": "Exposure Factor",
        "factor_probabilidad_tabla": "Probability Factor",
        "impacto_tabla": "Impact / Severity",
        "indice_criticidad": "Criticality Index",
    }
}

# Selección de idioma (sin cambiar nada más)
idioma_sel = st.selectbox("Idioma / Language", options=["es", "en"], index=0)
t = idiomas[idioma_sel]

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
    AgGrid(df, gridOptions=gridOptions, height=min(250, 35*len(df)), fit_columns_on_grid_load=True, enable_enterprise_modules=False, update_mode='NO_UPDATE')

if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual",
        "Amenaza Residual Ajustada", "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

# Layout principal: columnas izquierda, centro y derecha
col_izq, col_centro, col_der = st.columns([1.3, 2, 2])

with col_izq:
    mostrar_tabla_fija(tabla_efectividad[["Rango", "Mitigacion", "Descripcion"]], t["efectividad_controles"])
    mostrar_tabla_fija(tabla_exposicion[["Factor", "Nivel", "Descripcion"]], t["factor_exposicion_tabla"])
    mostrar_tabla_fija(tabla_probabilidad[["Factor", "Nivel", "Descripcion"]], t["factor_probabilidad_tabla"])
    mostrar_tabla_fija(tabla_impacto[["Nivel", "Valor", "Descripcion"]], t["impacto_tabla"])
    st.markdown(f"### {t['indice_criticidad']}")
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
    st.subheader(t["resultado"])

    nombre_riesgo = st.text_input(t["nombre_riesgo"])
    descripcion = st.text_area(t["descripcion_riesgo"])
    tipo_impacto = st.selectbox(
        t["tipo_impacto"],
        options=["Humano", "Ambiental", "Económico", "Operacional", "Infraestructura", "Tecnológico", "Reputacional", "Social", "Comercial"]
    )
    exposicion = st.selectbox(t["factor_exposicion"], options=tabla_exposicion["Factor"], format_func=lambda x: f"{x} - {tabla_exposicion.loc[tabla_exposicion['Factor']==x, 'Nivel'].values[0]}")
    probabilidad = st.selectbox(t["factor_probabilidad"], options=tabla_probabilidad["Factor"], format_func=lambda x: f"{x} - {tabla_probabilidad.loc[tabla_probabilidad['Factor']==x, 'Nivel'].values[0]}")
    amenaza_deliberada = st.selectbox(t["amenaza_deliberada"], options=[1, 2, 3], format_func=lambda x: {1:"Baja",2:"Intermedia",3:"Alta"}[x], index=0)
    efectividad = st.slider(t["efectividad_control"], 0, 100, 50)

    # Corrección aquí: lista fija para niveles de impacto
    impacto_niveles = [1, 2, 3, 4, 5]
    impacto_descripciones = [
        "No afecta significativamente",
        "Afectación menor",
        "Afectación parcial y temporal",
        "Afectación significativa",
        "Impacto serio o pérdida total"
    ]

    impacto = st.selectbox(
        t["impacto"],
        options=impacto_niveles,
        format_func=lambda x: f"{x} - {impacto_descripciones[x-1]}"
    )

    # Cálculos
    efec_norm = efectividad / 100
    amenaza_inherente = round(exposicion * probabilidad, 4)
    amenaza_residual = round(amenaza_inherente * (1 - efec_norm), 4)
    amenaza_residual_ajustada = round(amenaza_residual * amenaza_deliberada, 4)
    valor_impacto = tabla_impacto.loc[tabla_impacto["Nivel"] == impacto, "Valor"].values[0]
    riesgo_residual = round(amenaza_residual_ajustada * valor_impacto, 4)

    clasificacion, color = clasificar_criticidad(riesgo_residual)

    st.markdown(f"### {t['resultado']}:")
    st.write(f"- {t['amenaza_inherente']}: {amenaza_inherente}")
    st.write(f"- {t['amenaza_residual']}: {amenaza_residual}")
    st.write(f"- {t['amenaza_residual_ajustada']}: {amenaza_residual_ajustada}")
    st.write(f"- {t['riesgo_residual']}: {riesgo_residual}")
    st.write(f"- {t['clasificacion']}: **{clasificacion}** (Color: {color})")

    if st.button(t["agregar_riesgo"]) and nombre_riesgo.strip() != "":
        nuevo_riesgo = {
            "Nombre Riesgo": nombre_riesgo.strip(),
            "Descripción": descripcion.strip(),
            "Tipo Impacto": tipo_impacto,
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
    st.header(t["mapa_calor"])
    if not st.session_state.riesgos.empty:
        st.session_state.riesgos["Impacto Valor"] = st.session_state.riesgos["Impacto"].map(
            lambda x: tabla_impacto.loc[tabla_impacto["Nivel"] == x, "Valor"].values[0]
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
            cbar_kws={"label": "Probabilidad x Impacto"}
        )
        ax.set_xlabel("Probabilidad")
        ax.set_ylabel("Tipo de Impacto")
        st.pyplot(fig)
    else:
        st.info("Agrega riesgos para mostrar el mapa de calor.")

st.markdown(f"### {t['matriz_acumulativa']}")
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
        label=t["descargar_excel"],
        data=processed_data,
        file_name="matriz_riesgos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Agrega riesgos para mostrar la matriz acumulativa.")

