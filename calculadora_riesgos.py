import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# -------------------------------
# ENCABEZADO Y DESCRIPCIÓN
# -------------------------------
st.title("🧮 Evaluación de Riesgos")
descripcion = st.text_area("✏️ Describe brevemente el escenario o área evaluada:", "")

st.markdown("---")

# -------------------------------
# COLUMNA IZQUIERDA: Tablas de exposición y probabilidad
# -------------------------------
col1, col_central, col2 = st.columns([1.5, 3.5, 1.5])  # proporción ajustada

with col1:
    st.subheader("📊 Factor de Exposición")
    tabla_exposicion = pd.DataFrame({
        "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
        "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
        "Criterios": [
            "Exposición extremadamente rara",
            "Exposición ocasional (cada 10 años)",
            "Exposición algunas veces al año",
            "Exposición mensual",
            "Exposición frecuente o semanal"
        ]
    })
    st.dataframe(tabla_exposicion, use_container_width=True, hide_index=True)

    st.subheader("📈 Factor de Probabilidad")
    tabla_probabilidad = pd.DataFrame({
        "Factor": [0.05, 0.15, 0.30, 0.55, 0.85],
        "Nivel": ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"],
        "Criterios": [
            "En condiciones excepcionales",
            "Ha sucedido alguna vez",
            "Podría ocurrir ocasionalmente",
            "Probable en ocasiones",
            "Ocurre con frecuencia / inminente"
        ]
    })
    st.dataframe(tabla_probabilidad, use_container_width=True, hide_index=True)

# -------------------------------
# COLUMNA DERECHA: Tablas de severidad e impacto y controles
# -------------------------------
with col2:
    st.subheader("💥 Impacto / Severidad")
    tabla_impacto = pd.DataFrame({
        "Nivel": [1, 2, 3, 4, 5],
        "Valor": [5, 10, 30, 60, 85],
        "Clasificación": ["Insignificante", "Leve", "Moderado", "Grave", "Crítico"],
        "Criterios": [
            "No afecta significativamente",
            "Afectación menor",
            "Afectación parcial y temporal",
            "Afectación significativa",
            "Impacto serio o pérdida total"
        ]
    })
    st.dataframe(tabla_impacto, use_container_width=True, hide_index=True)

    st.subheader("🛡️ Efectividad de Controles")
    tabla_controles = pd.DataFrame({
        "Rango": ["0%", "1 - 20%", "21-40%", "41-60%", "61-81%", "81-95%", "96-100%"],
        "Factor": [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1],
        "Mitigación": ["Inefectiva", "Limitada", "Baja", "Intermedia", "Alta", "Muy Alta", "Total"],
        "Criterios": [
            "No reduce el riesgo",
            "Reduce solo en condiciones ideales",
            "Mitiga riesgos menores",
            "Control estándar con limitaciones",
            "Reduce significativamente el riesgo",
            "Control robusto y bien implementado",
            "Elimina casi todo el riesgo"
        ]
    })
    st.dataframe(tabla_controles, use_container_width=True, hide_index=True)

# -------------------------------
# COLUMNA CENTRAL: Mapa de Calor
# -------------------------------
with col_central:
    st.subheader("🔥 Mapa de Calor basado en Probabilidad e Impacto")

    niveles = ["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"]
    impacto_valores = [5, 10, 30, 60, 85]
    probabilidad_valores = [0.05, 0.15, 0.30, 0.55, 0.85]

    heatmap_data = [[p * i for i in impacto_valores] for p in probabilidad_valores]
    df_heatmap = pd.DataFrame(heatmap_data, index=niveles, columns=niveles)

    def color_from_val(val):
        if val <= 2:
            return "green"
        elif val <= 4:
            return "yellow"
        elif val <= 15:
            return "orange"
        else:
            return "red"

    colors = df_heatmap.applymap(color_from_val)

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(df_heatmap, annot=True, fmt=".1f", cmap=sns.color_palette(
        ["green", "yellow", "orange", "red"], as_cmap=True), cbar=False, ax=ax)
    ax.set_xlabel("Impacto")
    ax.set_ylabel("Probabilidad")
    st.pyplot(fig)

# -------------------------------
# ÍNDICE DE CRITICIDAD
# -------------------------------
st.markdown("---")
st.subheader("📉 Índice de Criticidad y Aceptabilidad")
st.markdown("""
| Índice de Criticidad | Clasificación | Color |
|----------------------|---------------|--------|
| ≤ 2                  | ACEPTABLE     | 🟢     |
| >2 hasta 4           | TOLERABLE     | 🟡     |
| >4 hasta 15          | INACEPTABLE   | 🟠     |
| >15                  | INADMISIBLE   | 🔴     |

**Aceptabilidad basada en la fórmula Q × U**
""")

