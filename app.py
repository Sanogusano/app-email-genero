import streamlit as st
import pandas as pd
import re
import unicodedata
import matplotlib.pyplot as plt
from PIL import Image

# Configuración de página
st.set_page_config(page_title="Clasificador de Género por Nombre", layout="centered", page_icon="👤")

# Cargar logo
logo = Image.open("logo.jpg")
st.image(logo, width=250)

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

# ---------------- FUNCIONES ------------------

@st.cache_data
def cargar_diccionario():
    df = pd.read_csv("latam_forenames.csv")
    df = df.drop_duplicates(subset="forename")
    df["forename"] = df["forename"].astype(str).str.lower().str.strip()
    df["forename"] = df["forename"].apply(remover_tildes)
    df["gender"] = df["gender"].astype(str).str.strip()
    return df[["forename", "gender"]]

def remover_tildes(texto):
    if not isinstance(texto, str):
        return texto
    texto = unicodedata.normalize("NFKD", texto)
    return "".join([c for c in texto if not unicodedata.combining(c)])

def extraer_nombre_desde_email(email, nombres_validos):
    try:
        user = str(email).split("@")[0].lower()
        user = remover_tildes(user)
        tokens = re.split(r"[.\-_0-9]+", user)
        for token in tokens:
            for nombre in nombres_validos:
                if nombre in token and len(nombre) >= 4:
                    return nombre
        return "No detectado"
    except:
        return "No detectado"

# ------------- EJECUCIÓN APP ----------------

archivo = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if archivo:
    try:
        df = pd.read_csv(archivo, encoding="latin-1", sep=";", on_bad_lines="skip")
        df.columns = df.columns.str.strip().str.lower()

        if "email" not in df.columns:
            st.error("❌ El archivo debe tener una columna llamada 'email'")
            st.stop()

        diccionario = cargar_diccionario()
        nombres_validos = set(diccionario["forename"].tolist())

        df["nombre_original"] = df["nombre"] if "nombre" in df.columns else ""
        df["nombre_original"] = df["nombre_original"].fillna("").astype(str).str.lower().apply(remover_tildes)

        df["nombre_detectado"] = df.apply(
            lambda row: row["nombre_original"] if row["nombre_original"] else extraer_nombre_desde_email(row["email"], nombres_validos),
            axis=1
        )

        df["fuente_nombre"] = df.apply(
            lambda row: "columna nombre" if row["nombre_original"] else (
                "correo electrónico" if row["nombre_detectado"] != "No detectado" else "no disponible"
            ),
            axis=1
        )

        df_final = df.merge(diccionario, how="left", left_on="nombre_detectado", right_on="forename")
        df_final["gender"] = df_final["gender"].fillna("No identificado")

        st.success("✅ Resultado del análisis")
        st.dataframe(df_final[["email", "nombre_detectado", "fuente_nombre", "gender"]])

        fig, ax = plt.subplots()
        df_final["gender"].value_counts().plot(kind='bar', ax=ax, color='mediumslateblue')
        ax.set_title("Distribución de Géneros Detectados")
        st.pyplot(fig)

        csv_final = df_final[["email", "nombre_detectado", "fuente_nombre", "gender"]].to_csv(index=False)
        st.download_button("📥 Descargar resultados", csv_final, file_name="genero_detectado.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
