import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO
from datetime import datetime
from fpdf import FPDF
import os
from matplotlib.colors import LinearSegmentedColormap
from st_aggrid import AgGrid, GridOptionsBuilder

# Configuración inicial de la página
st.set_page_config(layout="wide", page_title="Gestor de Riesgos Avanzado", page_icon="⚠️")

# =============================================
# 1. FUNCIONES AUXILIARES Y DEFINICIONES INICIALES
# =============================================

# Traducciones (es/en)
idiomas = {
    "es": {
        "titulo": "Calculadora de Riesgos Avanzada",
        "nombre_riesgo": "Nombre del riesgo",
        "descripcion": "Descripción del riesgo",
        # ... (completar con todas las traducciones del original)
    },
    "en": {
        "titulo": "Advanced Risk Calculator",
        "nombre_riesgo": "Risk Name",
        # ... (completar con todas las traducciones del original)
    }
}

# Tablas de referencia (efectividad, exposición, etc.)
tabla_efectividad = pd.DataFrame({
    "Rango": ["0%", "1-20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
    "Factor": [0, 0.1, 0.3, 0.5, 0.7, 0.9, 0.1],
    # ... (completar con las tablas originales)
})

# =============================================
# 2. INICIALIZACIÓN DEL DATAFRAME PRINCIPAL
# =============================================

def inicializar_dataframe():
    """Crea el DataFrame principal si no existe"""
    columnas_base = [
        "Nombre Riesgo", "Descripción", "Tipo Impacto", "Exposición", 
        "Probabilidad", "Amenaza Deliberada", "Efectividad Control (%)",
        "Impacto", "Amenaza Inherente", "Amenaza Residual", 
        "Amenaza Residual Ajustada", "Riesgo Residual",
        "Clasificación Criticidad", "Color Criticidad",
        "Prioridad", "Icono", "Fecha"
    ]
    
    if "riesgos" not in st.session_state:
        st.session_state.riesgos = pd.DataFrame(columns=columnas_base)
        
        # Datos de ejemplo (opcional)
        if st.session_state.riesgos.empty:
            ejemplos = [{
                "Nombre Riesgo": "Fuga de datos",
                "Tipo Impacto": "Tecnológico",
                "Riesgo Residual": 18.5,
                "Prioridad": "🔴 CRÍTICO",
                # ... otros campos
            }]
            st.session_state.riesgos = pd.concat([st.session_state.riesgos, pd.DataFrame(ejemplos)], ignore_index=True)

# =============================================
# 3. FUNCIONES PARA LAS MEJORAS SELECCIONADAS
# =============================================

# --- MEJORA 1: Sistema de Priorización Automatizada ---
def asignar_prioridad(riesgo_residual):
    """Asigna categoría de prioridad basada en el riesgo residual"""
    if riesgo_residual > 15:
        return {"Prioridad": "🔴 CRÍTICO", "Nivel": 4, "Color": "#FF0000"}
    elif riesgo_residual > 4:
        return {"Prioridad": "🟠 ALTO", "Nivel": 3, "Color": "#FF8C00"}
    elif riesgo_residual > 2:
        return {"Prioridad": "🟡 MEDIO", "Nivel": 2, "Color": "#FFD700"}
    else:
        return {"Prioridad": "🟢 BAJO", "Nivel": 1, "Color": "#008000"}

# --- MEJORA 6: Matriz de Riesgo Dinámica ---
def generar_matriz_riesgo(df):
    """Genera gráfico interactivo de matriz de riesgo"""
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

# --- MEJORA 7: Exportación Mejorada ---
def generar_pdf(df):
    """Genera reporte PDF profesional"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte de Riesgos", ln=1, align='C')
    
    # Tabla de riesgos
    pdf.set_font("Arial", size=10)
    for _, row in df.iterrows():
        pdf.cell(0, 10, f"{row['Nombre Riesgo']} - {row['Prioridad']}", ln=1)
    
    return pdf.output(dest='S').encode('latin-1')

# --- MEJORA 12: Historial de Cambios ---
def guardar_version():
    """Guarda snapshot del estado actual"""
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
    # Inicialización
    inicializar_dataframe()
    
    # Sidebar - Configuración
    with st.sidebar:
        st.title("⚙️ Configuración")
        idioma = st.radio("Idioma", ["Español", "English"], index=0)
        lang = "es" if idioma == "Español" else "en"
        t = idiomas[lang]
        
        # --- MEJORA 3: Filtros Avanzados ---
        with st.expander("🔍 Filtros", expanded=True):
            tipos_impacto = st.multiselect(
                t["tipo_impacto"],
                options=st.session_state.riesgos["Tipo Impacto"].unique(),
                default=st.session_state.riesgos["Tipo Impacto"].unique()
            )
            
            rango_riesgo = st.slider(
                "Rango de Riesgo Residual",
                min_value=0,
                max_value=int(st.session_state.riesgos["Riesgo Residual"].max() + 1),
                value=(0, int(st.session_state.riesgos["Riesgo Residual"].max() + 1))
            )
    
    # Contenido principal
    st.title(t["titulo"])
    
    # --- Formulario de entrada de riesgos ---
    with st.form("form_riesgo"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input(t["nombre_riesgo"])
            descripcion = st.text_area(t["descripcion"])
            tipo_impacto = st.selectbox(t["tipo_impacto"], ["Tecnológico", "Humano", "Operacional"])
        
        with col2:
            exposicion = st.slider(t["exposicion"], 0.0, 1.0, 0.5)
            probabilidad = st.slider(t["probabilidad"], 0.0, 1.0, 0.3)
            impacto = st.selectbox(t["impacto"], [1, 2, 3, 4, 5])
        
        if st.form_submit_button("➕ Agregar Riesgo"):
            # Cálculos de riesgo
            riesgo_residual = exposicion * probabilidad * impacto * 10  # Ejemplo simplificado
            
            # --- Aplicar MEJORA 1 ---
            prioridad = asignar_prioridad(riesgo_residual)
            
            nuevo_riesgo = {
                "Nombre Riesgo": nombre,
                "Descripción": descripcion,
                "Tipo Impacto": tipo_impacto,
                "Exposición": exposicion,
                "Probabilidad": probabilidad,
                "Impacto": impacto,
                "Riesgo Residual": riesgo_residual,
                **prioridad,
                "Fecha": datetime.now()
            }
            
            st.session_state.riesgos = pd.concat([
                st.session_state.riesgos,
                pd.DataFrame([nuevo_riesgo])
            ], ignore_index=True)
            
            # --- MEJORA 12: Guardar versión ---
            guardar_version()
            st.success("✅ Riesgo agregado correctamente!")
    
    # --- MEJORA 6: Matriz de Riesgo ---
    st.header("📊 Matriz de Riesgo")
    if not st.session_state.riesgos.empty:
        st.plotly_chart(
            generar_matriz_riesgo(st.session_state.riesgos), 
            use_container_width=True
        )
    else:
        st.info("No hay riesgos registrados para mostrar")
    
    # --- MEJORA 15: Modo Comparativo ---
    st.header("🔍 Comparar Riesgos")
    if not st.session_state.riesgos.empty:
        riesgos_comparar = st.multiselect(
            "Seleccionar riesgos para comparar",
            options=st.session_state.riesgos["Nombre Riesgo"].tolist(),
            default=st.session_state.riesgos["Nombre Riesgo"].head(2).tolist()
        )
        
        if len(riesgos_comparar) >= 2:
            df_comparacion = st.session_state.riesgos[
                st.session_state.riesgos["Nombre Riesgo"].isin(riesgos_comparar)
            ]
            st.dataframe(df_comparacion.style.background_gradient(
                subset=["Riesgo Residual"], 
                cmap="YlOrRd"
            ))
    
    # --- MEJORA 7: Exportación ---
    st.header("📤 Exportar Datos")
    if not st.session_state.riesgos.empty:
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            st.download_button(
                "💾 Excel (CSV)",
                data=st.session_state.riesgos.to_csv(index=False).encode('utf-8'),
                file_name="riesgos.csv",
                mime="text/csv"
            )
        
        with col_exp2:
            pdf_data = generar_pdf(st.session_state.riesgos)
            st.download_button(
                "📄 Reporte PDF",
                data=pdf_data,
                file_name="reporte_riesgos.pdf",
                mime="application/pdf"
            )
    
    # --- MEJORA 12: Historial ---
    if "historial" in st.session_state and st.session_state.historial:
        with st.expander("🕰️ Historial de Versiones"):
            st.write(f"Versiones guardadas: {len(st.session_state.historial)}")
            version_seleccionada = st.selectbox(
                "Seleccionar versión",
                options=range(len(st.session_state.historial)),
                format_func=lambda x: f"Versión {x+1} - {st.session_state.historial[x]['timestamp'].strftime('%d/%m/%Y %H:%M')}"
            )
            
            if st.button("⏳ Restaurar esta versión"):
                st.session_state.riesgos = st.session_state.historial[version_seleccionada]["data"].copy()
                st.rerun()

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
