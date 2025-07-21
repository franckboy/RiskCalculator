import streamlit as st
import pandas as pd
import numpy as np
import random
from io import BytesIO
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(layout="wide")

# CSS personalizado
st.markdown("""
<style>
/* Botones */
div.stButton > button {
    background-color: #28a745;
    color: white;
    font-weight: bold;
    height: 40px; width: 100%; border-radius: 5px; border: none;
    transition: background-color 0.3s ease;
}
div.stButton > button:hover {
    background-color: #218838; cursor: pointer;
}
/* Selectores */
div.stSelectbox > div[data-baseweb="select"] {
    width: 100% !important; font-size: 16px !important;
}
textarea { font-size: 16px !important; }
/* Responsive tabla */
@media (max-width: 768px) {
    .dataframe { overflow-x: auto; }
}
</style>
""", unsafe_allow_html=True)

# Tablas base
tabla_tipo_impacto = pd.DataFrame({
    "Código": ["H","O","E","I","T","R","A","C","S"],
    "Tipo de Impacto": ["Humano (H)","Operacional (O)","Económico (E)",
                        "Infraestructura (I)","Tecnológico (T)","Reputacional (R)",
                        "Ambiental (A)","Comercial (C)","Social (S)"],
    "Ponderación": [25,20,15,12,10,8,5,3,2],
    "Explicación ASIS": [
        "Máxima prioridad: Protección de empleados, visitantes y stakeholders físicos (ASIS enfatiza la seguridad personal).",
        "Continuidad del negocio: Interrupciones críticas en procesos (ORM.1 exige planes de recuperación).",
        "Pérdidas financieras directas: Robos, fraudes, parálisis de ingresos (impacto en sostenibilidad).",
        "Activos físicos: Daño a instalaciones, equipos o cadenas de suministro (ASIS prioriza protección física).",
        "Ciberseguridad y datos: Hackeos, fallos de sistemas (ASIS lo vincula a riesgos operacionales).",
        "Imagen pública: Crisis por incidentes de seguridad o ética (difícil de cuantificar, pero crítico).",
        "Solo relevante si aplica: Derrames, contaminación (mayor peso en industrias reguladas).",
        "Relaciones con clientes: Pérdida de contratos o confianza (menos urgente que otros).",
        "Impacto comunitario: Solo crítico en sectores con alta interacción social (ej. minería).",
    ]
})

factor_exposicion = pd.DataFrame({
    "Factor": [0.05,0.15,0.30,0.55,0.85],
    "Nivel": ["Muy Baja","Baja","Moderada","Alta","Muy Alta"],
    "Definición": [
        "Exposición extremadamente rara",
        "Exposición ocasional (cada 10 años)",
        "Exposición algunas veces al año",
        "Exposición mensual",
        "Exposición frecuente o semanal"
    ]
})

factor_probabilidad = pd.DataFrame({
    "Factor": [0.05,0.15,0.30,0.55,0.85],
    "Nivel": ["Muy Baja","Baja","Moderada","Alta","Muy Alta"],
    "Descripcion": [
        "En condiciones excepcionales","Ha sucedido alguna vez","Podría ocurrir ocasionalmente",
        "Probable en ocasiones","Ocurre con frecuencia / inminente"
    ]
})

criticidad_límites = [
    (0,0.7,"ACEPTABLE","#008000"),
    (0.7,3,"TOLERABLE","#FFD700"),
    (3,7,"INACEPTABLE","#FF8C00"),
    (7,float("inf"),"INADMISIBLE","#FF0000")
]

textos = {
    "es": {
        "nombre_riesgo":"Nombre del riesgo","descripcion_riesgo":"Descripción del riesgo",
        "tipo_impacto":"Tipo de impacto","justificacion":"Explicación según ASIS",
        "factor_exposicion":"Factor de exposición","factor_probabilidad":"Factor de probabilidad",
        "amenaza_deliberada":"Amenaza deliberada",
        "amenaza_deliberada_opciones":{1:"No",2:"Sí baja",3:"Sí alta"},
        "efectividad_control":"Efectividad del control (%)","impacto":"Impacto",
        "agregar_riesgo":"Agregar riesgo","exito_agregar":"Riesgo agregado exitosamente",
        "resultados":"Resultados","mapa_calor_titulo":"Mapa de Calor de Riesgos",
        "pareto_titulo":"Pareto - Riesgos Residuales",
        "matriz_acumulativa_titulo":"Matriz Acumulativa de Riesgos",
        "descargar_excel":"Descargar matriz en Excel",
        "info_agrega_riesgos":"Agrega riesgos para visualizar los gráficos.",
        "info_agrega_riesgos_matriz":"Agrega riesgos para mostrar la matriz acumulativa.",
        "stacked_titulo":"Gráfico de Barras Apiladas - Riesgo por Tipo de Impacto",
        "montecarlo_titulo":"Simulación de Monte Carlo",
        "num_iteraciones":"Número de iteraciones","probabilidad_min":"Probabilidad Mínima",
        "probabilidad_max":"Probabilidad Máxima","impacto_min":"Impacto Mínimo",
        "impacto_max":"Impacto Máximo"
    },
    "en": {
        "nombre_riesgo":"Risk Name","descripcion_riesgo":"Risk Description",
        "tipo_impacto":"Impact Type","justificacion":"Explanation according to ASIS",
        "factor_exposicion":"Exposure Factor","factor_probabilidad":"Probability Factor",
        "amenaza_deliberada":"Deliberate Threat",
        "amenaza_deliberada_opciones":{1:"No",2:"Low",3:"High"},
        "efectividad_control":"Control Effectiveness (%)","impacto":"Impact",
        "agregar_riesgo":"Add Risk","exito_agregar":"Risk added successfully",
        "resultados":"Results","mapa_calor_titulo":"Risk Heatmap",
        "pareto_titulo":"Pareto - Residual Risks",
        "matriz_acumulativa_titulo":"Accumulated Risk Matrix",
        "descargar_excel":"Download matrix as Excel",
        "info_agrega_riesgos":"Add risks to visualize charts.",
        "info_agrega_riesgos_matriz":"Add risks to show the accumulated matrix.",
        "stacked_titulo":"Stacked Bar Chart - Risk by Impact Type",
        "montecarlo_titulo":"Monte Carlo Simulation",
        "num_iteraciones":"Number of Iterations","probabilidad_min":"Minimum Probability",
        "probabilidad_max":"Maximum Probability","impacto_min":"Minimum Impact",
        "impacto_max":"Maximum Impact"
    }
}

# Estado persistente
if "riesgos" not in st.session_state:
    st.session_state.riesgos = pd.DataFrame(columns=[
        "Nombre Riesgo","Descripción","Tipo Impacto","Exposición","Probabilidad",
        "Amenaza Deliberada","Efectividad Control (%)","Impacto",
        "Amenaza Inherente","Amenaza Residual","Amenaza Residual Ajustada",
        "Riesgo Residual","Clasificación Criticidad","Color Criticidad"
    ])

# Sidebar: idioma
with st.sidebar:
    st.title("Opciones / Options")
    idioma = "es" if not st.checkbox("English / Inglés") else "en"

# Selección de idioma
if idioma == "es":
    t = textos["es"]
else:
    t = textos["en"]

# Columnas de UI
col_form, col_graf = st.columns([3,2])

# Funciones de cálculo y clasificación
def calcular_criticidad(p, e, a, ef, imp, pond):
    inh = p*e
    res = inh*(1-ef)
    res_aj = res*a
    return inh, res, res_aj, res_aj*imp*(pond/100)

def clasifica(v):
    for inf,sup,c,col in criticidad_límites:
        if inf < v <= sup: return c,col
    return "NO CLASIFICADO","#000000"

# Formulario principal
with col_form:
    st.title("Calculadora de Riesgos" if idioma=="es" else "Risk Calculator")
    st.subheader(t["resultados"])
    nombre = st.text_input(t["nombre_riesgo"])
    descripcion = st.text_area(t["descripcion_riesgo"])
    opts = tabla_tipo_impacto.apply(lambda r: f"{r['Código']} - {r['Tipo de Impacto']}", axis=1)
    sel = st.selectbox(t["tipo_impacto"], opts)
    cod = sel.split(" - ")[0]
    just = tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"]==cod, "Explicación ASIS"].values[0]
    pond = int(tabla_tipo_impacto.loc[tabla_tipo_impacto["Código"]==cod, "Ponderación"].values[0])
    st.markdown(f"**{t['justificacion']}:** {just}")
    expo = st.selectbox(t["factor_exposicion"], options=factor_exposicion["Factor"],
                        format_func=lambda x: f"{x:.2f} – {factor_exposicion.loc[factor_exposicion['Factor']==x, 'Nivel'].values[0]}")
    prob = st.selectbox(t["factor_probabilidad"], options=factor_probabilidad["Factor"],
                        format_func=lambda x: f"{x:.2f} – {factor_probabilidad.loc[factor_probabilidad['Factor']==x, 'Nivel'].values[0]}")
    amenaza_del = st.selectbox(t["amenaza_deliberada"], options=[1,2,3],
                               format_func=lambda x: t["amenaza_deliberada_opciones"][x], index=0)
    ef = st.slider(t["efectividad_control"], 0,100,50)
    imp = st.number_input(t["impacto"], 0,100,30,1)
    btn = st.button(t["agregar_riesgo"])

    st.subheader(t["matriz_acumulativa_titulo"])
    if st.session_state.riesgos.empty:
        st.info(t["info_agrega_riesgos_matriz"])
    else:
        df = st.session_state.riesgos.copy()
        styled = df.style.apply(lambda row: ["background-color:"+row["Color Criticidad"] if col=="Clasificación Criticidad" else "" for col in row.index], axis=1)
        st.dataframe(styled, use_container_width=True)
        def a_excel(df):
            buf = BytesIO()
            writer = pd.ExcelWriter(buf, engine="xlsxwriter")
            df.to_excel(writer, index=False, sheet_name="Matriz de Riesgos")
            writer.save()
            return buf.getvalue()
        st.download_button(label=t["descargar_excel"], data=a_excel(df),
                           file_name="matriz.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Procesar al agregar
if btn:
    if not nombre.strip():
        st.error("Debe ingresar un nombre para el riesgo." if idioma=="es" else "You must enter a risk name.")
    else:
        ef_n = ef/100
        inh,res,res_aj,resid = calcular_criticidad(prob,expo,amenaza_del,ef_n,imp,pond)
        clas,color = clasifica(resid)
        nuevo = {
            "Nombre Riesgo": nombre,"Descripción": descripcion,"Tipo Impacto": cod,
            "Exposición": expo,"Probabilidad": prob,"Amenaza Deliberada": amenaza_del,
            "Efectividad Control (%)": ef,"Impacto": imp,
            "Amenaza Inherente": inh,"Amenaza Residual": res,
            "Amenaza Residual Ajustada": res_aj,"Riesgo Residual": resid,
            "Clasificación Criticidad": clas,"Color Criticidad": color
        }
        st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo])],
                                            ignore_index=True)
        st.success(t["exito_agregar"])

# Visualización de gráficos
with col_graf:
    # Mapa de calor
    st.header(t["mapa_calor_titulo"])
    if st.session_state.riesgos.empty:
        st.info(t["info_agrega_riesgos"])
    else:
        dfh = st.session_state.riesgos.copy()
        dfh["Impacto Rango"] = pd.cut(dfh["Impacto"], bins=[0,20,40,60,80,100], labels=["0-20","21-40","41-60","61-80","81-100"], include_lowest=True)
        dfh["Riesgo Rango"] = pd.cut(dfh["Riesgo Residual"], bins=[0,0.7,3,7,float("inf")], labels=["0-0.7","0.7-3","3-7","7+"], include_lowest=True, right=False)
        heat = dfh.groupby(["Riesgo Rango","Impacto Rango"]).size().unstack(fill_value=0).reindex(["0-0.7","0.7-3","3-7","7+"],axis=0).reindex(["0-20","21-40","41-60","61-80","81-100"],axis=1)
        fig = go.Figure(go.Heatmap(z=heat.values, x=heat.columns, y=heat.index, colorscale=[(0,"green"),(0.5,"yellow"),(1,"red")]))
        fig.update_layout(title=t["mapa_calor_titulo"], xaxis_title="Rango Impacto", yaxis_title="Riesgo Residual", margin=dict(l=40,r=40,t=40,b=40))
        st.plotly_chart(fig, use_container_width=True)

    # Pareto
    st.header(t["pareto_titulo"])
    if st.session_state.riesgos.empty:
        st.info(t["info_agrega_riesgos"])
    else:
        dfp = st.session_state.riesgos.groupby("Nombre Riesgo")[["Riesgo Residual"]].sum().sort_values("Riesgo Residual", ascending=False)
        dfp["% Acum"] = dfp["Riesgo Residual"].cumsum()/dfp["Riesgo Residual"].sum()*100
        figp = go.Figure()
        figp.add_trace(go.Bar(x=dfp.index, y=dfp["Riesgo Residual"], name="Residual"))
        figp.add_trace(go.Scatter(x=dfp.index, y=dfp["% Acum"], mode="lines+markers", name="% Acum", yaxis="y2"))
        figp.update_layout(yaxis=dict(title="Riesgo Residual"), yaxis2=dict(title="% Acum", overlaying="y", side="right"), margin=dict(l=50,r=50,t=50,b=50), legend=dict(x=0.8,y=1.1))
        st.plotly_chart(figp, use_container_width=True)

    # Barras apiladas
    st.header(t["stacked_titulo"])
    if st.session_state.riesgos.empty:
        st.info(t["info_agrega_riesgos"])
    else:
        dfs = st.session_state.riesgos.groupby(["Tipo Impacto","Nombre Riesgo"])[["Riesgo Residual"]].sum().unstack(fill_value=0)
        dfs.columns = dfs.columns.get_level_values(1)
        figs = go.Figure()
        for r in dfs.columns:
            figs.add_trace(go.Bar(x=dfs.index, y=dfs[r], name=r))
        figs.update_layout(xaxis_title="Tipo Impacto", yaxis_title="Riesgo Residual", margin=dict(l=40,r=40,t=40,b=40), barmode="stack")
        st.plotly_chart(figs, use_container_width=True)

    # Monte Carlo
    st.header(t["montecarlo_titulo"])
    n_it = st.number_input(t["num_iteraciones"],100,10000,1000,100)
    p_min = st.number_input(t["probabilidad_min"],0.0,1.0,0.1,0.01)
    p_max = st.number_input(t["probabilidad_max"],0.0,1.0,0.3,0.01)
    i_min = st.number_input(t["impacto_min"],0,10000,1000,100)
    i_max = st.number_input(t["impacto_max"],0,10000,5000,100)

    def monte(pmin, pmax, imin, imax, n):
        return [random.uniform(pmin,pmax)*random.uniform(imin,imax) for _ in range(n)]

    res = monte(p_min,p_max,i_min,i_max,n_it)
    st.write(f"Riesgo promedio: {np.mean(res):.2f}")
    st.write(f"Riesgo máximo: {np.max(res):.2f}")
    st.write(f"Riesgo mínimo: {np.min(res):.2f}")
    st.write(f"Percentil 95: {np.percentile(res,95):.2f}")

    figh = go.Figure(data=[go.Histogram(x=res)])
    figh.update_layout(title="Distribución Monte Carlo", xaxis_title="Riesgo", yaxis_title="Frecuencia")
    st.plotly_chart(figh, use_container_width=True)
