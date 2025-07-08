import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from PIL import Image

# Configuración general
st.set_page_config(page_title="Género Match", layout="centered")

# Logo centrado
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    logo = Image.open("logo.jpg")  # Asegúrate de tener logo.jpg en el directorio
    st.image(logo, width=250)

# Título e instrucciones
st.markdown("### Clasificador de Género por Nombre")

st.markdown("""
Sube un archivo `.CSV` con las siguientes condiciones:

- Debe tener las columnas **email** y **nombre** (ambas en minúscula).
- Solo es válido para nombres comunes en Latinoamérica.
- El resultado descargable incluirá: **nombre**, **email** y **género** detectado.
""")

# Cargar diccionario
@st.cache_data
def cargar_diccionario():
    df = pd.read_csv("latam_forenames.csv")
    df = df.drop_duplicates(subset="forename")
    df["forename"] = df["forename"].str.lower().str.strip()
    df["gender"] = df["gender"].str.upper().str.strip()
    return df[["forename", "gender"]]

diccionario = cargar_diccionario()

# Subida del archivo
archivo = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

# Procesamiento
if archivo:
    try:
        df = pd.read_csv(archivo, encoding="utf-8", sep=";", on_bad_lines="skip")
        df.columns = df.columns.str.strip().str.lower()

        if not {"email", "nombre"}.issubset(df.columns):
            st.error("El archivo debe contener las columnas 'email' y 'nombre'")
            st.stop()

        df["nombre_limpio"] = df["nombre"].str.lower().str.strip()
        df["nombre_limpio"] = df["nombre_limpio"].str.replace(r"[^a-záéíóúüñ ]", "", regex=True)

        df_genero = df.merge(diccionario, how="left", left_on="nombre_limpio", right_on="forename")
        df_genero["gender"] = df_genero["gender"].fillna("No identificado")

        st.success("✅ Resultado del análisis")
        st.dataframe(df_genero[["nombre", "email", "gender"]])

        # Gráfico
        genero_counts = df_genero["gender"].value_counts()
        fig, ax = plt.subplots()
        genero_counts.plot(kind='bar', ax=ax, color='mediumslateblue')
        ax.set_title("Distribución de Géneros Detectados")
        ax.set_xlabel("Género")
        ax.set_ylabel("Cantidad")
        st.pyplot(fig)

        # Descarga
        csv_final = df_genero[["nombre", "email", "gender"]].to_csv(index=False)
        st.download_button("📥 Descargar resultados", csv_final, file_name="genero_detectado.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")

# Footer con créditos
st.markdown("---")
st.markdown("""
<p style='text-align: center; font-size: 0.9em; color: grey;'>
Copyright © 2025 - Andrés Restrepo · 
<a href='https://www.linkedin.com/in/andresrestrepoh/' target='_blank'>LinkedIn</a>
</p>
""", unsafe_allow_html=True)
