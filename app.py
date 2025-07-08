import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from PIL import Image

# Configuración general de la página
st.set_page_config(page_title="Clasificador de Género por Nombre", layout="centered")

# Logo y Título Personalizado
logo = Image.open("logo_monastery.png")  # Asegúrate de tener este archivo en tu directorio
st.image(logo, width=150)
st.markdown("<h1 style='color:#4B0082;'>Clasificador de Género por Nombre</h1>", unsafe_allow_html=True)
st.markdown("""
<p style='font-size:18px;'>Sube un archivo .CSV con una columna llamada <strong>Nombre</strong>. 
Este sistema usa un diccionario con más de 12 millones de nombres para identificar el género de cada entrada.</p>
""", unsafe_allow_html=True)

# Sidebar con info personal
with st.sidebar:
    st.markdown("### Sobre esta App")
    st.info("Desarrollado por Andrés Restrepo\n\nemail: andres@monastery.co\nIG: @andresrestrepo")
    st.markdown("---")
    st.markdown("**Repositorio en GitHub:** [github.com/andresrestrepo/app-genero](#)")

# CSS personalizado
st.markdown("""
    <style>
    body {
        background-color: #f9f9fb;
        font-family: 'Helvetica', sans-serif;
    }
    .stButton > button {
        background-color: #4B0082;
        color: white;
        border-radius: 8px;
    }
    .stMarkdown h1 {
        color: #4B0082;
    }
    .css-1v3fvcr { color: #4B0082; }
    </style>
""", unsafe_allow_html=True)

# Cargar diccionario
@st.cache_data
def cargar_diccionario():
    df = pd.read_csv("latam_forenames.csv")
    df = df.drop_duplicates(subset="forename")
    df["forename"] = df["forename"].astype(str).str.lower().str.strip()
    df["gender"] = df["gender"].astype(str).str.strip()
    return df[["forename", "gender"]]

diccionario = cargar_diccionario()

# Carga del archivo de usuario
archivo = st.file_uploader("\ud83d\udcc2 Sube tu archivo CSV", type=["csv"])

if archivo:
    try:
        df = pd.read_csv(archivo, encoding="utf-8", sep=";", on_bad_lines="skip")
        df.columns = df.columns.str.strip().str.lower()

        if "nombre" not in df.columns:
            st.error("El archivo debe tener una columna llamada 'Nombre'")
            st.stop()

        # Normalización del nombre
        with st.spinner("\ud83e\udde0 Analizando nombres..."):
            df["nombre_limpio"] = df["nombre"].str.lower().str.strip()
            df["nombre_limpio"] = df["nombre_limpio"].str.replace(r"[^a-záéíóúüñ ]", "", regex=True)
            df_genero = df.merge(diccionario, how="left", left_on="nombre_limpio", right_on="forename")
            df_genero["gender"] = df_genero["gender"].fillna("No identificado")

        st.success("\u2705 Resultado del análisis")
        st.dataframe(df_genero[["nombre", "gender"]])

        # Gráfico resumen
        genero_counts = df_genero["gender"].value_counts()
        fig, ax = plt.subplots()
        genero_counts.plot(kind='bar', ax=ax, color='mediumslateblue')
        ax.set_title("Distribución de Géneros Detectados")
        ax.set_xlabel("Género")
        ax.set_ylabel("Cantidad")
        st.pyplot(fig)

        # Descarga del archivo final
        csv_final = df_genero[["nombre", "gender"]].to_csv(index=False)
        st.download_button("\ud83d\udcc5 Descargar resultados", csv_final, file_name="genero_detectado.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")

# Pie de firma
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>\u00a9 2025 Andrés Restrepo – Desarrollado con \u2764\ufe0f y datos</p>", unsafe_allow_html=True)
