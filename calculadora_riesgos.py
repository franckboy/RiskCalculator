import streamlit as st
import pandas as pd
import numpy as np

# ---------------------------
# Definición de columnas base
# ---------------------------
columnas = [
    "ID Riesgo", "Nombre del Riesgo", "Amenaza", "Impacto", "Exposición (L+M)",
    "Probabilidad (N)", "Amenaza Inherente (S = Amenaza x Impacto)",
    "Impacto Normalizado (U)", "Riesgo Residual (W = S x U)",
    "Índice de Criticidad (AA)", "Multiplicador Criticidad (AC)",
    "Clasificación Control (K)", "Aceptabilidad (AB)",
    "Suma Riesgos por Bloque (Z)"
]

# ---------------------------
# Título de la app
# ---------------------------
st.set_page_config(page_title="Matriz de Riesgos", layout="wide")
st.title("Evaluación y Matriz de Riesgos")

# ---------------------------
# Cargar o inicializar la tabla
# ---------------------------
st.markdown("#### Ingresa los datos de los riesgos")

if "datos" not in st.session_state:
    df_vacio = pd.DataFrame(columns=columnas)
    st.session_state.datos = df_vacio

# ---------------------------
# Formulario para agregar un nuevo riesgo
# ---------------------------
with st.form("nuevo_riesgo"):
    col1, col2, col3 = st.columns(3)

    with col1:
        id_riesgo = st.text_input("ID Riesgo")
        nombre = st.text_input("Nombre del Riesgo")
        amenaza = st.number_input("Amenaza", min_value=0.0, max_value=5.0, step=0.1)
        impacto = st.number_input("Impacto", min_value=0.0, max_value=5.0, step=0.1)

    with col2:
        exposicion = st.number_input("Exposición (L+M)", min_value=0.0, max_value=10.0, step=0.1)
        probabilidad = st.number_input("Probabilidad (N)", min_value=0.0, max_value=10.0, step=0.1)
        impacto_norm = st.number_input("Impacto Normalizado (U)", min_value=0.0, max_value=5.0, step=0.1)
        multiplicador = st.number_input("Multiplicador Criticidad (AC)", min_value=0.0, max_value=5.0, step=0.1)

    with col3:
        clasificacion = st.selectbox("Clasificación Control (K)", ["Muy eficaz", "Eficaz", "Moderado", "Débil", "Inexistente"])
        aceptar = st.selectbox("Aceptabilidad (AB)", ["Aceptable", "Condicional", "No Aceptable"])
        suma_riesgo_bloque = 0  # lo calcularemos luego

    enviado = st.form_submit_button("Agregar riesgo")

    if enviado:
        amenaza_inherente = amenaza * impacto
        riesgo_residual = amenaza_inherente * impacto_norm
        indice_criticidad = riesgo_residual * multiplicador

        nuevo = pd.DataFrame([[id_riesgo, nombre, amenaza, impacto, exposicion,
                               probabilidad, amenaza_inherente, impacto_norm,
                               riesgo_residual, indice_criticidad, multiplicador,
                               clasificacion, aceptar, suma_riesgo_bloque]], columns=columnas)

        st.session_state.datos = pd.concat([st.session_state.datos, nuevo], ignore_index=True)
        st.success("✅ Riesgo agregado correctamente")

# ---------------------------
# Mostrar la matriz completa
# ---------------------------
if not st.session_state.datos.empty:
    st.markdown("### 🧾 Matriz de Riesgos Calculada")

    # Recalcular columna Z (suma de W por bloque de 9)
    df = st.session_state.datos.copy()
    df["Suma Riesgos por Bloque (Z)"] = df.index // 9
    z_vals = df.groupby("Suma Riesgos por Bloque (Z)")["Riesgo Residual (W = S x U)"].sum()
    df["Suma Riesgos por Bloque (Z)"] = df["Suma Riesgos por Bloque (Z)"].map(z_vals)

    st.dataframe(df, use_container_width=True, hide_index=True)

    with st.expander("📤 Exportar matriz a CSV"):
        st.download_button(
            label="Descargar CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="matriz_riesgos.csv",
            mime="text/csv"
        )
else:
    st.info("No hay riesgos registrados todavía. Usa el formulario de arriba para añadir uno.")
