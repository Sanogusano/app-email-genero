
import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from PIL import Image
import unicodedata
import time

# Configuración de la app
st.set_page_config(page_title="Clasificador de Género por Nombre", layout="centered", page_icon="👤")

# Cargar logo y encabezado
logo = Image.open("logo.jpg")
st.image(logo, width=250)
st.title("👤 Clasificador de Género por Nombre")
st.markdown("""
Sube un archivo .CSV con las columnas **email** y opcionalmente **nombre**.  
La app detectará el género a partir del nombre, o intentará extraerlo del correo si no está disponible.

✅ Solo válido para nombres en Latam.  
📥 El archivo de salida incluirá: **email**, **nombre_detectado**, **fuente_nombre**, **género**.

---  
📎 Puedes descargar un archivo de ejemplo para adaptar tu plantilla.  
🛡️ Copyright 2025 - Andrés Restrepo  
🔗 [linkedin.com/in/andresrestrepoh](https://www.linkedin.com/in/andresrestrepoh)
""")

# Función de normalización
def normalizar(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = re.sub(r"[^a-z]", "", texto)
    return texto

# Función mejorada para detectar nombre dentro del correo
def extraer_nombre_desde_email(email, nombres_validos):
    if pd.isna(email):
        return "Nombre no detectado"
    try:
        email_user = str(email).split("@")[0]
        email_user = normalizar(email_user)
        posibles = re.split(r"[\W\d_]+", email_user)
        posibles = [normalizar(frag) for frag in posibles if frag]

        for frag in posibles:
            if frag in nombres_validos:
                return frag
        for frag in posibles:
            for nombre in nombres_validos:
                if frag.startswith(nombre) and len(nombre) >= 5:
                    return nombre
        return "Nombre no detectado"
    except Exception:
        return "Nombre no detectado"

# Cargar diccionario
@st.cache_data
def cargar_diccionario():
    df = pd.read_csv("latam_forenames.csv")
    df = df.drop_duplicates(subset="forename")
    df["forename"] = df["forename"].apply(normalizar)
    df["gender"] = df["gender"].str.strip()
    return df[["forename", "gender"]]

diccionario = cargar_diccionario()
nombres_validos = diccionario["forename"].tolist()

# Subida de archivo
archivo = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

# Archivo de ejemplo descargable
ejemplo = pd.DataFrame({"email": ["juanperez@gmail.com", "mariarojas@hotmail.com"], "nombre": ["", ""]})
ejemplo_csv = ejemplo.to_csv(index=False, sep=";")
st.download_button("📄 Descargar ejemplo CSV", ejemplo_csv, file_name="ejemplo_clasificacion.csv", mime="text/csv")

if archivo:
    try:
        df = pd.read_csv(archivo, encoding="utf-8", sep=";", on_bad_lines="skip")
        df.columns = df.columns.str.strip().str.lower()

        if "email" not in df.columns:
            st.error("❌ El archivo debe tener una columna llamada 'email'")
            st.stop()

        df["nombre_original"] = df["nombre"] if "nombre" in df.columns else ""
        df["nombre_original"] = df["nombre_original"].fillna("").astype(str).str.strip().str.lower()
        df["nombre_original"] = df["nombre_original"].apply(normalizar)

        progress_bar = st.progress(0)
        total = len(df)
        resultados = []

        for i, row in df.iterrows():
            nombre_detectado = row["nombre_original"] if row["nombre_original"] != "" else extraer_nombre_desde_email(row["email"], nombres_validos)
            fuente = "columna nombre" if row["nombre_original"] != "" else ("correo electrónico" if nombre_detectado != "Nombre no detectado" else "no disponible")
            genero = diccionario.loc[diccionario["forename"] == nombre_detectado, "gender"].values
            genero = genero[0] if len(genero) > 0 else "No identificado"
            resultados.append([row["email"], nombre_detectado, fuente, genero])
            progress_bar.progress((i + 1) / total)

        df_final = pd.DataFrame(resultados, columns=["email", "nombre_detectado", "fuente_nombre", "gender"])

        st.success("✅ Resultado del análisis")
        st.dataframe(df_final)

        # Gráfico
        genero_counts = df_final["gender"].value_counts()
        fig, ax = plt.subplots()
        genero_counts.plot(kind='bar', ax=ax, color='mediumslateblue')
        ax.set_title("Distribución de Géneros Detectados")
        ax.set_xlabel("Género")
        ax.set_ylabel("Cantidad")
        st.pyplot(fig)

        # Descarga
        csv_export = df_final.to_csv(index=False)
        st.download_button("📥 Descargar resultados", csv_export, file_name="genero_detectado.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
