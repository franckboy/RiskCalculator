import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode

st.set_page_config(layout="wide", page_title="Risk Calculator / Calculadora de Riesgos")

# --- CSS personalizado para estilos ---
st.markdown("""
<style>
    .main {
        padding: 1rem 3rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    h1, h2, h3 {
        text-align: center;
        color: #004d40;
    }
    .stSlider > div > div > div > input {
        accent-color: #00796b;
    }
    .ag-theme-alpine {
        font-size: 12px !important;
    }
    .stButton>button {
        background-color: #00796b;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        margin-top: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #004d40;
        color: #b2dfdb;
    }
    .stTextInput>div>div>input {
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 0.3rem;
    }
    .stTextArea>div>textarea {
        border-radius: 5px;
        border: 1px solid #ccc;
        padding: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Definición de tablas fijas en español ---
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

# --- Traducciones de textos y tablas ---
textos = {
    "es": {
        "efectividad": "Efectividad de Controles",
        "exposicion": "Factor de Exposición",
        "probabilidad": "Factor de Probabilidad",
        "impacto": "Impacto / Severidad",
        "tipo_impacto": "Tipo de Impacto",
        "justificacion": "Justificación",
        "factor_exposicion": "Factor de Exposición",
        "factor_probabilidad": "Factor de Probabilidad",
        "factor_probabilidad_titulo": "Probabilidad",
        "tipo_impacto_titulo": "Tipo de Impacto",
        "amenaza_deliberada": "Amenaza Deliberada",
        "amenaza_deliberada_opciones": {1:"Baja", 2:"Intermedia", 3:"Alta"},
        "efectividad_control": "Efectividad del control (%)",
        "impacto": "Impacto",
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion_riesgo": "Descripción del riesgo",
        "resultados": "Resultados",
        "clasificacion": "Clasificación",
        "agregar_riesgo": "Agregar riesgo a la matriz",
        "exito_agregar": "Riesgo agregado a la matriz acumulativa.",
        "mapa_calor_titulo": "Mapa de Calor por Probabilidad Residual vs Impacto",
        "matriz_acumulativa_titulo": "Matriz Acumulativa de Riesgos",
        "descargar_excel": "Descargar matriz de riesgos en Excel",
        "info_agrega_riesgos": "Agrega riesgos para mostrar la matriz acumulativa.",
        "boton_limpiar": "Limpiar matriz de riesgos",
        "confirmar_borrar": "¿Seguro que quieres limpiar la matriz de riesgos? Esta acción no se puede deshacer.",
        "boton_descargar_pareto": "Descargar gráfico Pareto (PNG)",
        "filtro_nombre": "Filtrar por Nombre de Riesgo",
        "filtro_clasificacion": "Filtrar por Clasificación",
        "no_hay_riesgos": "No hay riesgos que coincidan con el filtro."
    },
    "en": {
        "efectividad": "Control Effectiveness",
        "exposicion": "Exposure Factor",
        "probabilidad": "Probability Factor",
        "impacto": "Impact / Severity",
        "tipo_impacto": "Impact Type",
        "justificacion": "Justification",
        "factor_exposicion": "Exposure Factor",
        "factor_probabilidad": "Probability Factor",
        "factor_probabilidad_titulo": "Probability",
        "tipo_impacto_titulo": "Impact Type",
        "amenaza_deliberada": "Deliberate Threat",
        "amenaza_deliberada_opciones": {1:"Low", 2:"Medium", 3:"High"},
        "efectividad_control": "Control Effectiveness (%)",
        "impacto": "Impact",
        "nombre_riesgo": "Risk Name",
        "descripcion_riesgo": "Risk Description",
        "resultados": "Results",
        "clasificacion": "Classification",
        "agregar_riesgo": "Add Risk to Matrix",
        "exito_agregar": "Risk added to cumulative matrix.",
        "mapa_calor_titulo": "Heatmap by Residual Probability vs Impact",
        "matriz_acumulativa_titulo": "Cumulative Risk Matrix",
        "descargar_excel": "Download Risk Matrix Excel",
        "info_agrega_riesgos": "Add risks to display the cumulative matrix.",
        "boton_limpiar": "Clear Risk Matrix",
        "confirmar_borrar": "Are you sure you want to clear the risk matrix? This action cannot be undone.",
        "boton_descargar_pareto": "Download Pareto Chart (PNG)",
        "filtro_nombre": "Filter by Risk Name",
        "filtro_clasificacion": "Filter by Classification",
        "no_hay_riesgos": "No risks match the filter."
    }
}

# --- Funciones para traducción de tablas fijas ---
def traducir_tabla(df, idioma):
    if idioma == "en":
        traducciones = {
            "Tipo de Impacto": "Impact Type",
            "Ponderación": "Weight",
            "Justificación": "Justification",
            "Rango": "Range",
            "Factor": "Factor",
            "Mitigacion": "Mitigation",
            "Descripcion": "Description",
            "Nivel": "Level",
            "Valor": "Value",
            "Clasificación": "Classification",
            "Límite Superior": "Upper Limit",
            "Color": "Color"
        }
        df = df.rename(columns=traducciones)
        # Traducción de valores específicos en columnas, si es necesario
        if "Nivel" in df.columns:
            nivel_traduccion = {
                "Muy Baja": "Very Low",
                "Baja": "Low",
                "Moderada": "Moderate",
                "Alta": "High",
                "Muy Alta": "Very High"
            }
            if "Nivel" in df.columns:
                df["Level"] = df["Nivel"].map(nivel_traduccion).fillna(df["Nivel"])
        if "Color" in df.columns:
            color_traduccion = {
                "Verde": "Green",
                "Amarillo": "Yellow",
                "Naranja": "Orange",
                "Rojo": "Red"
            }
            df["Color"] = df["Color"].map(color_traduccion).fillna(df["Color"])
    return df

# --- Función para clasificar criticidad ---
def clasificar_criticidad(valor, idioma="es"):
    if valor <= 2:
        return ("ACEPTABLE" if idioma=="es" else "ACCEPTABLE"), ("Verde" if idioma=="es" else "Green")
    elif valor <= 4:
        return ("TOLERABLE" if idioma=="es" else "TOLERABLE"), ("Amarillo" if idioma=="es" else "Yellow")
    elif valor <= 15:
        return ("INACEPTABLE" if idioma=="es" else "UNACCEPTABLE"), ("Naranja" if idioma=="es" else "Orange")
    else:
        return ("INADMISIBLE" if idioma=="es" else "INADMISSIBLE"), ("Rojo" if idioma=="es" else "Red")

# --- Función para mostrar tablas con AgGrid ---
def mostrar_tabla_fija(df, titulo):
    st.markdown(f"### {titulo}")
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True, filter=True, sortable=True)
    gb.configure_grid_options(domLayout='normal')
    gridOptions = gb.build()
    AgGrid(df, gridOptions=gridOptions, height=min(250, 35*len(df)), fit_columns_on_grid_load=True,
           enable_enterprise_modules=False, update_mode=GridUpdateMode.NO_UPDATE)

# --- Función cálculo criticidad ---
def calcular_criticidad(probabilidad, exposicion, amenaza_deliberada, efectividad, valor_impacto, ponderacion_impacto):
    amenaza_inherente = probabilidad * exposicion
    amenaza_residual = amenaza_inherente * (1 - efectividad)
    amenaza_residual_ajustada = amenaza_residual * amenaza_deliberada
    riesgo_residual = amenaza_residual_ajustada * valor_impacto * (ponderacion_impacto / 100)
    return amenaza_inherente, amenaza_residual, amenaza_residual_ajustada, riesgo_residual

# --- Cache para guardar riesgos ---
@st.cache_data(ttl=3600)
def inicializar_riesgos():
    return pd.DataFrame(columns=[
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", "Probabilidad", "Amenaza Deliberada",
        "Efectividad Control (%)", "Impacto", "Amenaza Inherente", "Amenaza Residual", "Amenaza Residual Ajustada",
        "Riesgo Residual", "Clasificación Criticidad", "Color Criticidad"
    ])

if "riesgos" not in st.session_state:
    st.session_state.riesgos = inicializar_riesgos()

# --- Sidebar: selector idioma y mostrar/ocultar ---
with st.sidebar:
    idioma = st.selectbox("Seleccione idioma / Select language", options=["es", "en"], index=0)
    mostrar_idioma = st.checkbox("Mostrar opciones de idioma / Show language options", value=True)
    st.markdown("---")
    if st.button(textos[idioma]["boton_limpiar"]):
        if st.confirm(textos[idioma]["confirmar_borrar"]):
            st.session_state.riesgos = inicializar_riesgos()
            st.success("Matriz de riesgos limpiada / Risk matrix cleared")

if not mostrar_idioma:
    st.sidebar.empty()

# --- Traducir tablas según idioma ---
tabla_tipo_impacto_mostrar = traducir_tabla(tabla_tipo_impacto, idioma)
tabla_efectividad_mostrar = traducir_tabla(tabla_efectividad, idioma)
tabla_exposicion_mostrar = traducir_tabla(tabla_exposicion, idioma)
tabla_probabilidad_mostrar = traducir_tabla(tabla_probabilidad, idioma)
tabla_impacto_mostrar = traducir_tabla(tabla_impacto, idioma)

# --- Layout principal ---
col_izq, col_centro, col_der = st.columns([1.3, 2, 2])

with col_izq:
    mostrar_tabla_fija(tabla_efectividad_mostrar[["Range" if idioma=="en" else "Rango",
                                                "Mitigation" if idioma=="en" else "Mitigacion",
                                                "Description" if idioma=="en" else "Descripcion"]],
                       textos[idioma]["efectividad"])
    mostrar_tabla_fija(tabla_exposicion_mostrar[["Factor",
                                                "Level" if idioma=="en" else "Nivel",
                                                "Description" if idioma=="en" else "Descripcion"]],
                       textos[idioma]["exposicion"])
    mostrar_tabla_fija(tabla_probabilidad_mostrar[["Factor",
                                                  "Level" if idioma=="en" else "Nivel",
                                                  "Description" if idioma=="en" else "Descripcion"]],
                       textos[idioma]["probabilidad"])
    mostrar_tabla_fija(tabla_impacto_mostrar[["Nivel" if idioma=="es" else "Level",
                                             "Valor" if idioma=="es" else "Value",
                                             "Descripcion" if idioma=="es" else "Description"]],
                       textos[idioma]["impacto"])
    mostrar_tabla_fija(tabla_tipo_impacto_mostrar, textos[idioma]["tipo_impacto"])
    st.markdown(f"### {textos[idioma]['clasificacion']} de Criticidad")
    crit_display = tabla_criticidad.drop(columns=["Color"])
    if idioma == "en":
        crit_display = crit_display.rename(columns={"Límite Superior": "Upper Limit", "Clasificación": "Classification"})
    st.table(crit_display)
    st.markdown("""
        <ul>
            <li style='color:green;'>Verde / Green: Aceptable / Acceptable (≤ 2)</li>
            <li style='color:gold;'>Amarillo / Yellow: Tolerable (≤ 4)</li>
            <li style='color:orange;'>Naranja / Orange: Inaceptable / Unacceptable (≤ 15)</li>
            <li style='color:red;'>Rojo / Red: Inadmisible / Inadmissible (> 15)</li>
        </ul>
    """, unsafe_allow_html=True)

with col_centro:
    st.title("Calculadora de Riesgos / Risk Calculator")
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

    clasificacion, color = clasificar_criticidad(riesgo_residual, idioma)

    st.markdown(f"### {textos[idioma]['resultados']}:")
    st.write(f"- Amenaza Inherente / Inherent Threat: {amenaza_inherente:.4f}")
    st.write(f"- Amenaza Residual / Residual Threat: {amenaza_residual:.4f}")
    st.write(f"- Amenaza Residual Ajustada (x Amenaza Deliberada) / Adjusted Residual Threat (x Deliberate Threat): {amenaza_residual_ajustada:.4f}")
    st.write(f"- Riesgo Residual / Residual Risk: {riesgo_residual:.4f}")
    st.write(f"- Clasificación / Classification: **{clasificacion}** (Color: {color})")

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
        st.success(textos[idioma]["exito_agregar"])

with col_der:
    st.header(textos[idioma]["mapa_calor_titulo"])

    if not st.session_state.riesgos.empty:
        # Calcular matriz para heatmap con probabilidad residual vs impacto
        matriz_calor = st.session_state.riesgos.pivot_table(
            index="Tipo Impacto",
            columns="Probabilidad",
            values="Amenaza Residual",
            aggfunc=np.mean
        ).fillna(0).sort_index()

        # Crear heatmap
        colors = ["#008000", "#FFD700", "#FF8C00", "#FF0000"]
        cmap = LinearSegmentedColormap.from_list("criticidad_cmap", colors, N=256)

        fig, ax = plt.subplots(figsize=(7,5))
        sns.heatmap(
            matriz_calor,
            annot=True,
            fmt=".3f",
            cmap=cmap,
            cbar_kws={"label": f"{textos[idioma]['factor_probabilidad_titulo']} Residual"}
        )
        ax.set_xlabel(textos[idioma]["factor_probabilidad_titulo"])
        ax.set_ylabel(textos[idioma]["tipo_impacto_titulo"])
        st.pyplot(fig)

        # --- Gráfico Pareto ---
        st.header("Pareto Chart / Gráfico Pareto")

        riesgos_ordenados = st.session_state.riesgos.sort_values(by="Riesgo Residual", ascending=False).reset_index(drop=True)
        riesgos_ordenados["% Riesgo Individual"] = 100 * riesgos_ordenados["Riesgo Residual"] / riesgos_ordenados["Riesgo Residual"].sum()
        riesgos_ordenados["% Riesgo Acumulado"] = riesgos_ordenados["% Riesgo Individual"].cumsum()

        fig2, ax1 = plt.subplots(figsize=(8,5))
        barras = ax1.bar(riesgos_ordenados["Nombre Riesgo"], riesgos_ordenados["% Riesgo Individual"], color="#00796b")
        ax1.set_ylabel('% Risk Individual / % Riesgo Individual', color='green')
        ax1.tick_params(axis='y', labelcolor='green')
        plt.xticks(rotation=45, ha='right')
        ax2 = ax1.twinx()
        ax2.plot(riesgos_ordenados["Nombre Riesgo"], riesgos_ordenados["% Riesgo Acumulado"], color='red', marker='o')
        ax2.set_ylabel('% Cumulative Risk / % Riesgo Acumulado', color='red')
        ax2.set_ylim(0, 110)

        st.pyplot(fig2)

        # Botón para descargar gráfico Pareto PNG
        buf = BytesIO()
        fig2.savefig(buf, format="png", bbox_inches='tight')
        buf.seek(0)
        st.download_button(
            label=textos[idioma]["boton_descargar_pareto"],
            data=buf,
            file_name="pareto_chart.png",
            mime="image/png"
        )

        # --- Filtros para matriz acumulativa ---
        st.header(textos[idioma]["matriz_acumulativa_titulo"])

        filtro_nombre = st.text_input(textos[idioma]["filtro_nombre"])
        filtro_clasificacion = st.multiselect(
            textos[idioma]["filtro_clasificacion"],
            options=st.session_state.riesgos["Clasificación Criticidad"].unique().tolist()
        )

        df_filtrado = st.session_state.riesgos.copy()
        if filtro_nombre:
            df_filtrado = df_filtrado[df_filtrado["Nombre Riesgo"].str.contains(filtro_nombre, case=False, na=False)]
        if filtro_clasificacion:
            df_filtrado = df_filtrado[df_filtrado["Clasificación Criticidad"].isin(filtro_clasificacion)]

        if df_filtrado.empty:
            st.info(textos[idioma]["no_hay_riesgos"])
        else:
            gb = GridOptionsBuilder.from_dataframe(df_filtrado)
            gb.configure_default_column(resizable=True, wrapText=True, autoHeight=True, filter=True, sortable=True)
            gb.configure_pagination(enabled=True)
            gridOptions = gb.build()
            AgGrid(
                df_filtrado,
                gridOptions=gridOptions,
                height=400,
                fit_columns_on_grid_load=True,
                theme="alpine"
            )

        # --- Exportar matriz acumulativa a Excel (con tablas fijas) ---
        towrite = BytesIO()
        with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
            st.session_state.riesgos.to_excel(writer, sheet_name="Riesgos", index=False)
            tabla_impacto_mostrar.to_excel(writer, sheet_name="Tabla Impacto", index=False)
            tabla_efectividad_mostrar.to_excel(writer, sheet_name="Tabla Efectividad", index=False)
            tabla_exposicion_mostrar.to_excel(writer, sheet_name="Tabla Exposición", index=False)
            tabla_probabilidad_mostrar.to_excel(writer, sheet_name="Tabla Probabilidad", index=False)
            tabla_tipo_impacto_mostrar.to_excel(writer, sheet_name="Tabla Tipo Impacto", index=False)
            # No es necesario writer.save() dentro de "with"
            processed_data = towrite.getvalue()

        st.download_button(
            label=textos[idioma]["descargar_excel"],
            data=processed_data,
            file_name="matriz_riesgos.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info(textos[idioma]["info_agrega_riesgos"])
