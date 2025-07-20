import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------
# DATOS BASE FIJOS
# --------------------
with st.sidebar:
    st.title("Tablas de Referencia")

    # Ejemplo tabla de impacto
    tabla_impacto = pd.DataFrame({
        "Código": ["H", "A", "E", "O", "I", "T", "R", "S", "C"],
        "Tipo de Impacto": [
            "Humano", "Ambiental", "Económico", "Operacional",
            "Infraestructura", "Tecnológico", "Reputacional", "Social", "Comercial"
        ],
        "Ponderación": [100, 85, 80, 75, 65, 60, 50, 45, 40],
        "Justificación": [
            "Afecta vida, salud o integridad. ISO 45001",
            "Daños ecológicos irreversibles. ISO 14001",
            "Pérdidas financieras. COSO ERM",
            "Interrupción de procesos críticos. ISO 22301",
            "Daño físico a instalaciones.",
            "Fallas de sistemas o ciberataques. ISO 27005",
            "Afecta imagen pública. COSO ERM",
            "Impacta comunidades. ISO 26000",
            "Pérdida de clientes o mercado."
        ]
    })
    st.markdown("### Tipos de Impacto")
    AgGrid(tabla_impacto, fit_columns_on_grid_load=True)

# ----------------------
# SECCIÓN CENTRAL
# ----------------------
with st.container():
    st.title("Calculadora de Riesgos")

    st.subheader("Descripción del Riesgo")
    descripcion = st.text_input("Describe brevemente el riesgo")

    tipo_riesgo = st.selectbox("Tipo de Impacto", options=tabla_impacto["Tipo de Impacto"])
    ponderacion_impacto = tabla_impacto[tabla_impacto["Tipo de Impacto"] == tipo_riesgo]["Ponderación"].values[0]

    st.markdown(f"**Ponderación Seleccionada:** {ponderacion_impacto}")

    exposicion = st.slider("Factor de exposición", min_value=1, max_value=5)
    probabilidad = st.slider("Factor de probabilidad", min_value=1, max_value=5)
    amenaza_deliberada = st.selectbox("Amenaza deliberada", [1, 2, 3])

    riesgo_residual = exposicion * probabilidad * amenaza_deliberada
    indice_criticidad = riesgo_residual * ponderacion_impacto

    st.metric("Riesgo Residual", riesgo_residual)
    st.metric("Índice de Criticidad", indice_criticidad)

# ----------------------
# GRÁFICOS A LA DERECHA
# ----------------------
col1, col2, col3 = st.columns([1, 0.1, 1])

with col3:
    st.subheader("Mapa de Calor")

    heat_data = np.zeros((5, 5))
    heat_data[probabilidad - 1, int(ponderacion_impacto / 20) - 1] = indice_criticidad

    fig, ax = plt.subplots()
    sns.heatmap(heat_data, cmap="YlOrRd", annot=True, fmt=".0f", cbar=True, ax=ax)
    ax.set_title("Probabilidad vs Impacto")
    ax.set_xlabel("Impacto")
    ax.set_ylabel("Probabilidad")
    st.pyplot(fig)

    st.subheader("Diagrama de Pareto (Ejemplo)")
    categorias = ["H", "A", "E", "O", "I", "T", "R", "S", "C"]
    valores = tabla_impacto["Ponderación"].values
    pareto_df = pd.DataFrame({"Categoría": categorias, "Valor": valores})
    pareto_df = pareto_df.sort_values(by="Valor", ascending=False)
    pareto_df["Acumulado"] = pareto_df["Valor"].cumsum()

    fig2, ax2 = plt.subplots()
    ax2.bar(pareto_df["Categoría"], pareto_df["Valor"], color="skyblue")
    ax2.plot(pareto_df["Categoría"], pareto_df["Acumulado"], color="red", marker="o")
    ax2.set_ylabel("Valor")
    ax2.set_title("Diagrama de Pareto")
    st.pyplot(fig2)

# ----------------------
# MATRIZ ACUMULATIVA ABAJO
# ----------------------
with st.container():
    st.subheader("Matriz Acumulativa de Riesgos")
    matriz = pd.DataFrame({
        "Riesgo": [descripcion],
        "Tipo": [tipo_riesgo],
        "Impacto": [ponderacion_impacto],
        "Exposición": [exposicion],
        "Probabilidad": [probabilidad],
        "Amenaza": [amenaza_deliberada],
        "Residual": [riesgo_residual],
        "Criticidad": [indice_criticidad]
    })
    AgGrid(matriz, fit_columns_on_grid_load=True)
