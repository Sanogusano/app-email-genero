import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from PIL import Image

# Configuración de la app
st.set_page_config(page_title="Clasificador de Género por Nombre", layout="centered", page_icon="👤")

# Logo
logo = Image.open("logo.jpg")
st.image(logo, width=250)

# Título e instrucciones
st.title("👤 Clasificador de Género por Nombre")
st.markdown("""
Sube un archivo .CSV con las columnas **email** y opcionalmente **nombre**.  
La app detectará el género a partir del nombre, o intentará extraerlo del correo si no está disponible.

✅ Solo válido para nombres en Latam.  
📥 El archivo de salida incluirá: **email**, **nombre_detectado**, **fuente_nombre**, **género**.

---
🛡️ Copyright 2025 - Andrés Restrepo  
🔗 [linkedin.com/in/andresrestrepoh](https://www.linkedin.com/in/andresrestrepoh)
""")

# Cargar diccionario
@st.cache_data
def cargar_diccionario():
    df = pd.read_csv("latam_forenames.csv")
    df = df.drop_duplicates(subset="forename")
    df["forename"] = df["forename"].str.lower().str.strip()
    df["gender"] = df["gender"].str.strip()
    return df[["forename", "gender"]]

diccionario = cargar_diccionario()
nombres_validos = diccionario["forename"].tolist()

# Función para extraer nombre del email
def extraer_nombre_desde_email(email, nombres_validos):
    if pd.isna(email):
        return "Nombre no detectado"
    try:
        email_str = str(email).split("@")[0].lower()
        for nombre in nombres_validos:
            if nombre in email_str:
                return nombre
        return "Nombre no detectado"
    except Exception:
        return "Nombre no detectado"

# Cargar archivo
archivo = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if archivo:
    try:
        # Probar con separador ; y fallback a ,
        try:
            df = pd.read_csv(archivo, encoding="utf-8", sep=";")
        except:
            df = pd.read_csv(archivo, encoding="utf-8", sep=",")

        df.columns = df.columns.str.strip().str.lower()

        if "email" not in df.columns:
            st.error("❌ El archivo debe tener una columna llamada 'email'")
            st.stop()

        df["email"] = df["email"].fillna("").astype(str).str.strip().str.lower()
        df["nombre_original"] = df["nombre"] if "nombre" in df.columns else ""
        df["nombre_original"] = df["nombre_original"].fillna("").astype(str).str.strip().str.lower()

        # Detección de nombre
        df["nombre_detectado"] = df.apply(
            lambda row: row["nombre_original"] if row["nombre_original"] != "" else extraer_nombre_desde_email(row["email"], nombres_validos),
            axis=1
        )

        # Fuente del nombre
        df["fuente_nombre"] = df.apply(
            lambda row: "columna nombre" if row["nombre_original"] != "" else (
                "correo electrónico" if row["nombre_detectado"] != "Nombre no detectado" else "no disponible"
            ),
            axis=1
        )

        # Cruce con diccionario
        df_final = df.merge(diccionario, how="left", left_on="nombre_detectado", right_on="forename")
        df_final["gender"] = df_final["gender"].fillna("No identificado")

        # Mostrar resultado
        st.success("✅ Resultado del análisis")
        st.dataframe(df_final[["email", "nombre_detectado", "fuente_nombre", "gender"]])

        # Gráfico
        genero_counts = df_final["gender"].value_counts()
        fig, ax = plt.subplots()
        genero_counts.plot(kind='bar', ax=ax, color='mediumslateblue')
        ax.set_title("Distribución de Géneros Detectados")
        ax.set_xlabel("Género")
        ax.set_ylabel("Cantidad")
        st.pyplot(fig)

        # Descarga
        csv_export = df_final[["email", "nombre_detectado", "fuente_nombre", "gender"]].to_csv(index=False)
        st.download_button("📥 Descargar resultados", csv_export, file_name="genero_detectado.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
