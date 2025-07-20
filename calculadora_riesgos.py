import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

# -------------------------------
# TEXTOS TRADUCIDOS
# -------------------------------
textos = {
    "es": {
        "factor_exposicion_titulo": "Factor de Exposición",
        "factor_probabilidad_titulo": "Factor de Probabilidad",
        "impacto_severidad_titulo": "Impacto / Severidad",
        "tipo_impacto_titulo": "Tipo de Impacto y Justificación",
        "indice_criticidad_titulo": "Índice de Criticidad",
        "indice_criticidad_descripcion": """
            <ul>
                <li style='color:green;'>Verde: Aceptable (≤ 2)</li>
                <li style='color:gold;'>Amarillo: Tolerable (≤ 4)</li>
                <li style='color:orange;'>Naranja: Inaceptable (≤ 15)</li>
                <li style='color:red;'>Rojo: Inadmisible (> 15)</li>
            </ul>
        """,
        "resultados": "Resultados",
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion_riesgo": "Descripción del riesgo",
        "tipo_impacto": "Tipo de Impacto",
        "justificacion": "Justificación",
        "factor_exposicion": "Factor de Exposición",
        "factor_probabilidad": "Factor de Probabilidad",
        "amenaza_deliberada": "Amenaza Deliberada",
        "amenaza_deliberada_opciones": {1: "Baja", 2: "Intermedia", 3: "Alta"},
        "efectividad_control": "Efectividad del control (%)",
        "impacto": "Impacto",
        "amenaza_inherente": "Amenaza Inherente",
        "amenaza_residual": "Amenaza Residual",
        "amenaza_residual_ajustada": "Amenaza Residual Ajustada (x Amenaza Deliberada)",
        "riesgo_residual": "Riesgo Residual",
        "clasificacion": "Clasificación",
        "agregar_riesgo": "Agregar riesgo a la matriz",
        "exito_agregar": "Riesgo agregado a la matriz acumulativa.",
        "mapa_calor_titulo": "Mapa de Calor por Tipo de Impacto y Probabilidad vs Impacto",
        "info_agrega_riesgos": "Agrega riesgos para mostrar el mapa de calor.",
        "matriz_acumulativa_titulo": "Matriz Acumulativa de Riesgos",
        "info_agrega_riesgos_matriz": "Agrega riesgos para mostrar la matriz acumulativa.",
        "descargar_excel": "Descargar matriz de riesgos en Excel",
        "evaluacion_riesgos": "🛡️ Evaluación de Riesgos",
        "probabilidad_residual": "Probabilidad residual",
        "limpiar_matriz": "🗑️ Limpiar Matriz",
        "matriz_limpia": "✅ Matriz acumulativa limpiada correctamente.",
        "sin_datos": "🟡 No hay datos acumulados todavía."
    },
    "en": {
        "factor_exposicion_titulo": "Exposure Factor",
        "factor_probabilidad_titulo": "Probability Factor",
        "impacto_severidad_titulo": "Impact / Severity",
        "tipo_impacto_titulo": "Impact Type and Justification",
        "indice_criticidad_titulo": "Criticality Index",
        "indice_criticidad_descripcion": """
            <ul>
                <li style='color:green;'>Green: Acceptable (≤ 2)</li>
                <li style='color:gold;'>Yellow: Tolerable (≤ 4)</li>
                <li style='color:orange;'>Orange: Unacceptable (≤ 15)</li>
                <li style='color:red;'>Red: Inadmissible (> 15)</li>
            </ul>
        """,
        "resultados": "Results",
        "nombre_riesgo": "Risk Name",
        "descripcion_riesgo": "Risk Description",
        "tipo_impacto": "Impact Type",
        "justificacion": "Justification",
        "factor_exposicion": "Exposure Factor",
        "factor_probabilidad": "Probability Factor",
        "amenaza_deliberada": "Deliberate Threat",
        "amenaza_deliberada_opciones": {1: "Low", 2: "Intermediate", 3: "High"},
        "efectividad_control": "Control Effectiveness (%)",
        "impacto": "Impact",
        "amenaza_inherente": "Inherent Threat",
        "amenaza_residual": "Residual Threat",
        "amenaza_residual_ajustada": "Adjusted Residual Threat (x Deliberate Threat)",
        "riesgo_residual": "Residual Risk",
        "clasificacion": "Classification",
        "agregar_riesgo": "Add risk to matrix",
        "exito_agregar": "Risk added to the cumulative matrix.",
        "mapa_calor_titulo": "Heatmap by Impact Type and Probability vs Impact",
        "info_agrega_riesgos": "Add risks to show the heatmap.",
        "matriz_acumulativa_titulo": "Cumulative Risk Matrix",
        "info_agrega_riesgos_matriz": "Add risks to show the cumulative matrix.",
        "descargar_excel": "Download risk matrix in Excel",
        "evaluacion_riesgos": "🛡️ Risk Assessment",
        "probabilidad_residual": "Residual probability",
        "limpiar_matriz": "🗑️ Clear Matrix",
        "matriz_limpia": "✅ Matrix cleared successfully.",
        "sin_datos": "🟡 No data accumulated yet."
    }
}

# -------------------------------
# TABLAS DE REFERENCIA
# -------------------------------
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

# -------------------------------
# FUNCIONES
# -------------------------------
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

def color_criticidad(valor):
    if valor >= 0.6:
        return "background-color: red; color: white;"
    elif valor >= 0.3:
        return "background-color: orange; color: black;"
    else:
        return "background-color: green; color: white;"

# -------------------------------
# INICIALIZAR SESIÓN
# -------------------------------
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

if "matriz_acumulada" not in st.session_state:
    st.session_state["matriz_acumulada"] = []

# -------------------------------
# INTERFAZ PRINCIPAL
# -------------------------------
# Selector idioma en sidebar
with st.sidebar.expander("Language / Idioma", expanded=True):
    idioma = st.selectbox("Selecciona idioma / Select language", options=["es", "en"], index=0)

# Layout principal
col_izq, col_centro, col_der = st.columns([1.3, 2, 2])

with col_izq:
    mostrar_tabla_fija(tabla_efectividad[["Rango", "Mitigacion", "Descripcion"]], textos[idioma]["factor_exposicion_titulo"])
    mostrar_tabla_fija(tabla_exposicion[["Factor", "Nivel", "Descripcion"]], textos[idioma]["factor_probabilidad_titulo"])
    mostrar_tabla_fija(tabla_probabilidad[["Factor", "Nivel", "Descripcion"]], textos[idioma]["impacto_severidad_titulo"])
    mostrar_tabla_fija(tabla_tipo_impacto, textos[idioma]["tipo_impacto_titulo"])
    st.markdown(f"### {textos[idioma]['indice_criticidad_titulo']}")
    crit_display = tabla_criticidad.drop(columns=["Color"])
    st.table(crit_display)
    st.markdown(textos[idioma]["indice_criticidad_descripcion"], unsafe_allow_html=True)

with col_centro:
    st.title(textos[idioma]["evaluacion_riesgos"])
    
    # Sección de entrada de riesgo detallada
    st.subheader(textos[idioma]["resultados"])
    nombre_riesgo = st.text_input(textos[idioma]["nombre_riesgo"])
    descripcion = st.text_area(textos[idioma]["descripcion_riesgo"])

    opciones_impacto_visibles = tabla_tipo_impacto.apply(
        lambda row: f"{row['Código']} - {row['Tipo de Impacto']}", axis=1).tolist()
    seleccion_impacto = st.selectbox(textos[idioma]["tipo_impacto"], opciones_impacto_visibles)
    codigo_impacto = seleccion_impacto.split(" - ")[0]
    justificacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Justificación"].values[0]
    ponderacion_impacto = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"] == codigo_impacto, "Ponderación"].values[0]
    st.markdown(f"**{textos[idioma]['justificacion']}:** {justificacion_impacto}")

    exposicion = st.selectbox(
        textos[idioma]["factor_exposicion"],
        options=tabla_exposicion["Factor"],
        format_func=lambda x: f"{x} - {tabla_exposicion.loc[tabla_exposicion['Factor']==x, 'Nivel'].values[0]}"
    )
    probabilidad = st.selectbox(
        textos[idioma]["factor_probabilidad"],
        options=tabla_probabilidad["Factor"],
        format_func=lambda x: f"{x} - {tabla_probabilidad.loc[tabla_probabilidad['Factor']==x, 'Nivel'].values[0]}"
    )
    amenaza_deliberada = st.selectbox(
        textos[idioma]["amenaza_deliberada"],
        options=[1, 2, 3],
        format_func=lambda x: textos[idioma]["amenaza_deliberada_opciones"][x],
        index=0
    )
    efectividad = st.slider(textos[idioma]["efectividad_control"], 0, 100, 50)

    impacto = st.selectbox(
        textos[idioma]["impacto"],
        options=tabla_impacto["Nivel"],
        format_func=lambda x: f"{x} - {tabla_impacto.loc[tabla_impacto['Nivel']==x, 'Descripcion'].values[0]}"
    )

    efectividad_norm = efectividad / 100
    valor_impacto = tabla_impacto.loc[tabla_impacto["Nivel"] == impacto, "Valor"].values[0]

    amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual = calcular_criticidad(
        probabilidad, exposicion, amenaza_deliberada, efectividad_norm, valor_impacto, ponderacion_impacto
    )

    clasificacion, color = clasificar_criticidad(riesgo_residual)

    st.markdown(f"### {textos[idioma]['resultados']}:")
    st.write(f"- {textos[idioma]['amenaza_inherente']}: {amenaza_inherente:.4f}")
    st.write(f"- {textos[idioma]['amenaza_residual']}: {amenaza_residual:.4f}")
    st.write(f"- {textos[idioma]['amenaza_residual_ajustada']}: {amenaza_residual_ajustada:.4f}")
    st.write(f"- {textos[idioma]['riesgo_residual']}: {riesgo_residual:.4f}")
    st.write(f"- {textos[idioma]['clasificacion']}: **{clasificacion}** (Color: {color})")

    if st.button(textos[idioma]["agregar_riesgo"]) and nombre_riesgo.strip() != "":
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
        
        # También agregar a la matriz simple
        nuevo_simple = {
            "Riesgo": nombre_riesgo.strip(),
            "Probabilidad": amenaza_residual_ajustada,
            "Impacto": valor_impacto / 100,  # Normalizado a 0-1
            "Índice de Criticidad": riesgo_residual / 100  # Normalizado a 0-1
        }
        st.session_state["matriz_acumulada"].append(nuevo_simple)
        
        st.success(textos[idioma]["exito_agregar"])
        st.experimental_rerun()

    # Sección simple de entrada de riesgo
    st.markdown("---")
    st.subheader("Entrada rápida de riesgo")
    riesgo = st.text_input("Nombre del riesgo (simple)")
    probabilidad_simple = st.slider(textos[idioma]["probabilidad_residual"], 0.01, 1.0, 0.5)
    impacto_simple = st.slider(textos[idioma]["impacto"], 0.01, 1.0, 0.5)

    if st.button("Agregar riesgo simple"):
        if riesgo.strip() != "":
            criticidad = round(probabilidad_simple * impacto_simple, 4)
            nuevo = {
                "Riesgo": riesgo,
                "Probabilidad": probabilidad_simple,
                "Impacto": impacto_simple,
                "Índice de Criticidad": criticidad
            }
            st.session_state["matriz_acumulada"].append(nuevo)
            st.success("✅ Riesgo agregado correctamente.")
            st.experimental_rerun()
        else:
            st.warning("⚠️ Ingresa un nombre para el riesgo.")

with col_der:
    # Mapa de calor
    st.header(textos[idioma]["mapa_calor_titulo"])
    if not st.session_state.riesgos.empty:
        st.session_state.riesgos["Valor Mapa"] = (
            st.session_state.riesgos["Amenaza Residual"] *
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
            cmap="YlOrRd",
            cbar_kws={"label": textos[idioma]["mapa_calor_titulo"]}
        )
        ax.set_xlabel(textos[idioma]["factor_probabilidad_titulo"])
        ax.set_ylabel(textos[idioma]["tipo_impacto_titulo"])
        st.pyplot(fig)
    else:
        st.info(textos[idioma]["info_agrega_riesgos"])

    # Matriz acumulativa
    st.markdown(f"## 📊 {textos[idioma]['matriz_acumulativa_titulo']}")
    with st.expander("🔽 Mostrar/Ocultar matriz acumulada"):
        if st.session_state["matriz_acumulada"]:
            df_acumulada = pd.DataFrame(st.session_state["matriz_acumulada"])
            
            # Mostrar con AgGrid
            gb_acumulada = GridOptionsBuilder.from_dataframe(df_acumulada)
            gb_acumulada.configure_pagination()
            gb_acumulada.configure_default_column(resizable=True, wrapText=True, autoHeight=True)
            gb_acumulada.configure_grid_options(domLayout='normal')
            grid_acumulada = gb_acumulada.build()

            AgGrid(
                df_acumulada.style.applymap(color_criticidad, subset=["Índice de Criticidad"]),
                gridOptions=grid_acumulada,
                allow_unsafe_jscode=True,
                theme="alpine",
                height=350,
                fit_columns_on_grid_load=False,
                use_container_width=True
            )

            # Botón para descargar Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                st.session_state.riesgos.to_excel(writer, sheet_name='Matriz de Riesgos', index=False)
                df_acumulada.to_excel(writer, sheet_name='Matriz Simple', index=False)
            st.download_button(
                label=textos[idioma]["descargar_excel"],
                data=output.getvalue(),
                file_name="matriz_riesgos.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            if st.button(textos[idioma]["limpiar_matriz"]):
                st.session_state["matriz_acumulada"] = []
                st.session_state.riesgos = pd.DataFrame(columns=[
                    "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
                    "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
                    "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
                ])
                st.success(textos[idioma]["matriz_limpia"])
                st.experimental_rerun()
        else:
            st.info(textos[idioma]["sin_datos"])
