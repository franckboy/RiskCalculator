import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from io import BytesIO
from datetime import datetime
from fpdf import FPDF

# Configuración inicial de la página
st.set_page_config(layout="wide", page_title="Gestor de Riesgos Avanzado", page_icon="⚠️")

# =============================================
# 1. FUNCIONES AUXILIARES Y DEFINICIONES INICIALES
# =============================================

# Traducciones (es/en) completas para la app
idiomas = {
    "es": {
        "titulo": "Calculadora de Riesgos Avanzada",
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion": "Descripción del riesgo",
        "tipo_impacto": "Tipo de Impacto",
        "exposicion": "Factor de Exposición",
        "probabilidad": "Factor de Probabilidad",
        "impacto": "Impacto",
        "agregar_riesgo": "➕ Agregar Riesgo",
        "filtros": "🔍 Filtros",
        "rango_riesgo": "Rango de Riesgo Residual",
        "comparar_riesgos": "🔍 Comparar Riesgos",
        "exportar_datos": "📤 Exportar Datos",
        "historial_versiones": "🕰️ Historial de Versiones",
        "restaurar_version": "⏳ Restaurar esta versión",
        "no_riesgos": "No hay riesgos registrados para mostrar",
        "seleccionar_riesgos": "Seleccionar riesgos para comparar",
    },
    "en": {
        "titulo": "Advanced Risk Calculator",
        "nombre_riesgo": "Risk Name",
        "descripcion": "Risk Description",
        "tipo_impacto": "Impact Type",
        "exposicion": "Exposure Factor",
        "probabilidad": "Probability Factor",
        "impacto": "Impact",
        "agregar_riesgo": "➕ Add Risk",
        "filtros": "🔍 Filters",
        "rango_riesgo": "Residual Risk Range",
        "comparar_riesgos": "🔍 Compare Risks",
        "exportar_datos": "📤 Export Data",
        "historial_versiones": "🕰️ Version History",
        "restaurar_version": "⏳ Restore this version",
        "no_riesgos": "No risks recorded to display",
        "seleccionar_riesgos": "Select risks to compare",
    }
}

# =============================================
# 2. INICIALIZACIÓN DEL DATAFRAME PRINCIPAL
# =============================================

def inicializar_dataframe():
    columnas_base = [
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", 
        "Probabilidad", "Amenaza Deliberada", "Efectividad Control (%)",
        "Impacto", "Amenaza Inherente", "Amenaza Residual", 
        "Amenaza Residual Ajustada", "Riesgo Residual",
        "Clasificación Criticidad", "Color Criticidad",
        "Prioridad", "Nivel", "Fecha"
    ]
    if "riesgos" not in st.session_state:
        st.session_state.riesgos = pd.DataFrame(columns=columnas_base)
        # Ejemplo inicial opcional
        ejemplo = {
            "Nombre Riesgo": "Fuga de datos",
            "Descripción": "Pérdida de información confidencial",
            "Tipo Impacto": "Tecnológico",
            "Exposición": 0.5,
            "Probabilidad": 0.4,
            "Amenaza Deliberada": 1,
            "Efectividad Control (%)": 50,
            "Impacto": 4,
            "Amenaza Inherente": 0.2,
            "Amenaza Residual": 0.1,
            "Amenaza Residual Ajustada": 0.1,
            "Riesgo Residual": 18.5,
            "Clasificación Criticidad": "INADMISIBLE",
            "Color Criticidad": "#FF0000",
            "Prioridad": "🔴 CRÍTICO",
            "Nivel": 4,
            "Fecha": datetime.now()
        }
        st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([ejemplo])], ignore_index=True)

# =============================================
# 3. FUNCIONES PARA LA GESTIÓN DE RIESGOS Y EXPORTACIÓN
# =============================================

def asignar_prioridad(riesgo_residual):
    if riesgo_residual > 15:
        return {"Prioridad": "🔴 CRÍTICO", "Nivel": 4, "Color Criticidad": "#FF0000"}
    elif riesgo_residual > 4:
        return {"Prioridad": "🟠 ALTO", "Nivel": 3, "Color Criticidad": "#FF8C00"}
    elif riesgo_residual > 2:
        return {"Prioridad": "🟡 MEDIO", "Nivel": 2, "Color Criticidad": "#FFD700"}
    else:
        return {"Prioridad": "🟢 BAJO", "Nivel": 1, "Color Criticidad": "#008000"}

def clasificar_criticidad(riesgo):
    if riesgo <= 2:
        return "ACEPTABLE"
    elif riesgo <= 4:
        return "TOLERABLE"
    elif riesgo <= 15:
        return "INACEPTABLE"
    else:
        return "INADMISIBLE"

def generar_matriz_riesgo(df):
    fig = px.scatter(
        df,
        x="Probabilidad",
        y="Impacto",
        color="Prioridad",
        size="Riesgo Residual",
        hover_name="Nombre Riesgo",
        hover_data=["Descripción", "Tipo Impacto"],
        color_discrete_map={
            "🔴 CRÍTICO": "#FF0000",
            "🟠 ALTO": "#FF8C00",
            "🟡 MEDIO": "#FFD700",
            "🟢 BAJO": "#008000"
        }
    )
    fig.update_layout(title="Matriz de Riesgo Interactiva")
    return fig

def generar_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Riesgos", ln=1, align='C')
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        pdf.cell(0, 10, f"{row['Nombre Riesgo']} - {row['Prioridad']} - Riesgo: {row['Riesgo Residual']:.2f}", ln=1)
    return pdf.output(dest='S').encode('latin-1')

def guardar_version():
    if "historial" not in st.session_state:
        st.session_state.historial = []
    st.session_state.historial.append({
        "timestamp": datetime.now(),
        "data": st.session_state.riesgos.copy()
    })

# =============================================
# 4. INTERFAZ PRINCIPAL DE LA APLICACIÓN
# =============================================

def main():
    # Inicializar datos
    inicializar_dataframe()
    
    # Sidebar configuración e idioma
    with st.sidebar:
        st.title("⚙️ Configuración")
        idioma = st.radio("Idioma / Language", ["Español", "English"], index=0)
        lang = "es" if idioma == "Español" else "en"
        t = idiomas[lang]
        
        with st.expander(t["filtros"], expanded=True):
            opciones_impacto = st.session_state.riesgos["Tipo Impacto"].unique().tolist() if not st.session_state.riesgos.empty else []
            tipos_impacto = st.multiselect(
                t["tipo_impacto"],
                options=opciones_impacto,
                default=opciones_impacto
            )
            rango_max = int(st.session_state.riesgos["Riesgo Residual"].max()) if not st.session_state.riesgos.empty else 10
            rango_riesgo = st.slider(
                t["rango_riesgo"],
                0, rango_max, (0, rango_max)
            )
    
    # Título principal
    st.title(t["titulo"])
    
    # Formulario para agregar riesgo
    with st.form("form_riesgo"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input(t["nombre_riesgo"])
            descripcion = st.text_area(t["descripcion"])
            tipo_impacto = st.selectbox(t["tipo_impacto"], ["Tecnológico", "Humano", "Operacional", "Ambiental", "Económico", "Infraestructura", "Reputacional", "Social", "Comercial"])
        with col2:
            exposicion = st.slider(t["exposicion"], 0.0, 1.0, 0.5, 0.05)
            probabilidad = st.slider(t["probabilidad"], 0.0, 1.0, 0.3, 0.05)
            impacto = st.selectbox(t["impacto"], [1, 2, 3, 4, 5])
        
        if st.form_submit_button(t["agregar_riesgo"]):
            amenaza_inherente = round(exposicion * probabilidad, 4)
            efectividad_control = 0.5  # Por defecto o futuro input
            amenaza_residual = round(amenaza_inherente * (1 - efectividad_control), 4)
            amenaza_residual_ajustada = amenaza_residual  # Si quieres incluir amenaza deliberada, modifícalo aquí
            
            riesgo_residual = round(amenaza_residual_ajustada * impacto * 10, 4)  # Escala ajustable
            
            clasificacion = clasificar_criticidad(riesgo_residual)
            prioridad_info = asignar_prioridad(riesgo_residual)
            
            nuevo_riesgo = {
                "Nombre Riesgo": nombre.strip(),
                "Descripción": descripcion.strip(),
                "Tipo Impacto": tipo_impacto,
                "Exposición": exposicion,
                "Probabilidad": probabilidad,
                "Amenaza Deliberada": 1,
                "Efectividad Control (%)": efectividad_control * 100,
                "Impacto": impacto,
                "Amenaza Inherente": amenaza_inherente,
                "Amenaza Residual": amenaza_residual,
                "Amenaza Residual Ajustada": amenaza_residual_ajustada,
                "Riesgo Residual": riesgo_residual,
                "Clasificación Criticidad": clasificacion,
                "Color Criticidad": prioridad_info["Color Criticidad"],
                "Prioridad": prioridad_info["Prioridad"],
                "Nivel": prioridad_info["Nivel"],
                "Fecha": datetime.now()
            }
            
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame([nuevo_riesgo])], ignore_index=True)
            guardar_version()
            st.success("✅ Riesgo agregado correctamente!")

    # Filtro aplicación de filtros activos
    riesgos_filtrados = st.session_state.riesgos[
        (st.session_state.riesgos["Tipo Impacto"].isin(tipos_impacto)) &
        (st.session_state.riesgos["Riesgo Residual"] >= rango_riesgo[0]) &
        (st.session_state.riesgos["Riesgo Residual"] <= rango_riesgo[1])
    ] if not st.session_state.riesgos.empty else pd.DataFrame()
    
    # Matriz de riesgo interactiva
    st.header("📊 Matriz de Riesgo")
    if not riesgos_filtrados.empty:
        fig = generar_matriz_riesgo(riesgos_filtrados)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t["no_riesgos"])
    
    # Comparar riesgos
    st.header(t["comparar_riesgos"])
    if not riesgos_filtrados.empty:
       

