import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import plotly.express as px
from io import BytesIO
from fpdf import FPDF

# ---------------------------------------------
# DATOS FIJOS PARA TABLAS Y TRADUCCIONES
# ---------------------------------------------
IDIOMAS = {
    "es": {
        "Impacto": [
            "No afecta significativamente",
            "Afectación menor",
            "Afectación parcial y temporal",
            "Afectación significativa",
            "Impacto serio o pérdida total"
        ],
        "Probabilidad": [
            "Muy poco probable",
            "Poco probable",
            "Moderadamente probable",
            "Probable",
            "Muy probable"
        ],
        "Exposición": [
            "Rara vez expuesto",
            "Ocasionalmente expuesto",
            "Frecuentemente expuesto"
        ],
        "Riesgo": "Calculadora de Riesgos",
        "Idioma": "Idioma",
        "Exportar": "Exportar a Excel",
        "ExportarPDF": "Exportar a PDF",
        "Graficos": "Gráficos de Riesgo",
        "Agregar": "Agregar riesgo",
        "NombreRiesgo": "Nombre del riesgo",
        "AmenazaDeliberada": "¿Amenaza deliberada?",
        "Editar": "Editar",
        "Eliminar": "Eliminar",
        "ProbabilidadResidual": "Probabilidad Residual",
        "ImpactoUsuario": "Impacto definido por usuario",
        "MatrizRiesgo": "Matriz de Riesgo (Heatmap)"
    },
    "en": {
        "Impacto": [
            "No significant impact",
            "Minor impact",
            "Partial and temporary impact",
            "Significant impact",
            "Severe impact or total loss"
        ],
        "Probabilidad": [
            "Very unlikely",
            "Unlikely",
            "Moderately likely",
            "Likely",
            "Very likely"
        ],
        "Exposición": [
            "Rarely exposed",
            "Occasionally exposed",
            "Frequently exposed"
        ],
        "Riesgo": "Risk Calculator",
        "Idioma": "Language",
        "Exportar": "Export to Excel",
        "ExportarPDF": "Export to PDF",
        "Graficos": "Risk Charts",
        "Agregar": "Add risk",
        "NombreRiesgo": "Risk name",
        "AmenazaDeliberada": "Deliberate threat?",
        "Editar": "Edit",
        "Eliminar": "Delete",
        "ProbabilidadResidual": "Residual Probability",
        "ImpactoUsuario": "User Defined Impact",
        "MatrizRiesgo": "Risk Matrix (Heatmap)"
    }
}

# -----------------------------
# FUNCIONES DE EXPORTACIÓN PDF
# -----------------------------
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Reporte de Riesgos', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

def generar_pdf(df):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for i, row in df.iterrows():
        texto = f"{row['Nombre Riesgo']} - Impacto: {row['Impacto']} - Probabilidad Residual: {row['Probabilidad Residual']} - Criticidad: {row['Criticidad']}"
        pdf.cell(0, 10, texto, ln=True)
    return pdf.output(dest='S').encode('latin-1')

# -----------------------------
# SELECCIÓN DE IDIOMA
# -----------------------------
def obtener_idioma():
    return st.sidebar.selectbox("🌐 Idioma / Language", options=["es", "en"], format_func=lambda x: "Español" if x == "es" else "English")

# -----------------------------
# APP PRINCIPAL
# -----------------------------
def main():
    st.set_page_config(layout="wide")
    idioma = obtener_idioma()
    textos = IDIOMAS[idioma]

    st.title(textos["Riesgo"])

    # Inicializar sesión de datos
    if "datos" not in st.session_state:
        st.session_state.datos = pd.DataFrame(columns=[
            "Nombre Riesgo", "Impacto", "Probabilidad", "Exposición", "Amenaza Deliberada", "Probabilidad Residual", "Criticidad"
        ])

    # Entrada de parámetros para nuevo riesgo
    col1, col2, col3 = st.columns(3)

    with col1:
        impacto = st.selectbox(
            f"{textos['Impacto'][0]} - {textos['Impacto'][-1]}",
            options=list(range(1, 6)),
            format_func=lambda x: f"{x} - {textos['Impacto'][x - 1]}",
            help="Seleccione el nivel de impacto del riesgo."
        )
    with col2:
        probabilidad = st.selectbox(
            f"{textos['Probabilidad'][0]} - {textos['Probabilidad'][-1]}",
            options=list(range(1, 6)),
            format_func=lambda x: f"{x} - {textos['Probabilidad'][x - 1]}",
            help="Seleccione la probabilidad inherente antes de controles."
        )
    with col3:
        exposicion = st.selectbox(
            f"{textos['Exposición'][0]} - {textos['Exposición'][-1]}",
            options=list(range(1, 4)),
            format_func=lambda x: f"{x} - {textos['Exposición'][x - 1]}",
            help="Seleccione el nivel de exposición al riesgo."
        )

    amenaza_deliberada = st.checkbox(textos["AmenazaDeliberada"], value=False)

    nombre_riesgo = st.text_input(textos["NombreRiesgo"])

    # Impacto ajustable para matriz heatmap
    impacto_usuario = st.slider(textos["ImpactoUsuario"], 1, 5, 3)

    # Calcular probabilidad residual (se podría ajustar según controles; aquí simplificado)
    probabilidad_residual = probabilidad
    if amenaza_deliberada:
        probabilidad_residual *= 1.5
        if probabilidad_residual > 5:
            probabilidad_residual = 5  # Limitar máximo

    # Calcular criticidad
    criticidad = impacto_usuario * probabilidad_residual

    # Botón para agregar riesgo
    if st.button(textos["Agregar"]) and nombre_riesgo.strip():
        nuevo = {
            "Nombre Riesgo": nombre_riesgo.strip(),
            "Impacto": impacto,
            "Probabilidad": probabilidad,
            "Exposición": exposicion,
            "Amenaza Deliberada": amenaza_deliberada,
            "Probabilidad Residual": round(probabilidad_residual, 2),
            "Criticidad": round(criticidad, 2)
        }
        st.session_state.datos = pd.concat([st.session_state.datos, pd.DataFrame([nuevo])], ignore_index=True)
        st.success(f"Riesgo '{nombre_riesgo}' agregado!")

    # Mostrar tabla editable con AgGrid (permite editar y eliminar)
    if not st.session_state.datos.empty:
        gb = GridOptionsBuilder.from_dataframe(st.session_state.datos)
        gb.configure_default_column(resizable=True, filter=False, sortable=True, editable=True)
        gb.configure_selection('multiple', use_checkbox=True)
        grid_options = gb.build()

        grid_response = AgGrid(
            st.session_state.datos,
            gridOptions=grid_options,
            height=300,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            allow_unsafe_jscode=True,
            fit_columns_on_grid_load=True,
            enable_enterprise_modules=False
        )

        # Actualizar datos con cambios hechos en la tabla
        st.session_state.datos = pd.DataFrame(grid_response['data'])

        # Botón para eliminar filas seleccionadas
        selected = grid_response['selected_rows']
        if selected:
            if st.button(textos["Eliminar"]):
                selected_names = [row["Nombre Riesgo"] for row in selected]
                st.session_state.datos = st.session_state.datos[~st.session_state.datos["Nombre Riesgo"].isin(selected_names)]
                st.success(f"{len(selected_names)} riesgos eliminados.")

        # Exportar Excel y PDF
        buffer = BytesIO()
        st.session_state.datos.to_excel(buffer, index=False)
        st.download_button(
            textos["Exportar"],
            data=buffer.getvalue(),
            file_name="riesgos.xlsx",
            mime="application/vnd.ms-excel"
        )

        pdf_data = generar_pdf(st.session_state.datos)
        st.download_button(
            textos["ExportarPDF"],
            data=pdf_data,
            file_name="riesgos.pdf",
            mime="application/pdf"
        )

        # Mostrar matriz de riesgo (heatmap) basada en probabilidad residual vs impacto usuario
        st.subheader(textos["MatrizRiesgo"])

        heatmap_df = st.session_state.datos.groupby(["Probabilidad Residual", "Impacto"]).size().reset_index(name='Cantidad')

        # Crear matriz pivot para heatmap
        pivot = heatmap_df.pivot(index="Impacto", columns="Probabilidad Residual", values="Cantidad").fillna(0)

        fig = px.imshow(
            pivot,
            labels=dict(x="Probabilidad Residual", y="Impacto", color="Cantidad"),
            x=pivot.columns,
            y=pivot.index[::-1],  # Para que impacto mayor esté arriba
            color_continuous_scale="YlOrRd"
        )
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
