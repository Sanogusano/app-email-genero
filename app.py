import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from PIL import Image

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

🛡️ Copyright 2025 - Andrés Restrepo  
🔗 [linkedin.com/in/andresrestrepoh](https://www.linkedin.com/in/andresrestrepoh)
""")

# Cargar diccionario desde CSV local
@st.cache_data
def cargar_diccionario():
    df = pd.read_csv("latam_forenames.csv")
    df = df.drop_duplicates(subset="forename")
    df["forename"] = df["forename"].astype(str).str.lower().str.strip()
    df["gender"] = df["gender"].astype(str).str.strip()
    return df[["forename", "gender"]]

diccionario = cargar_diccionario()
nombres_validos = set(diccionario["forename"].tolist())

# Función optimizada para detectar nombre dentro del correo
def extraer_nombre_desde_email(email):
    if not isinstance(email, str) or "@" not in email:
        return "Nombre no detectado"

    email_user = email.split("@")[0].lower()

    # Reemplazar puntos, guiones y otros por espacios
    email_user = re.sub(r"[\W\d_]+", " ", email_user)
    palabras = [p.strip() for p in email_user.split() if p.strip()]

    # Prioridad 1: palabra exacta en el diccionario
    for palabra in palabras:
        if palabra in nombres_validos:
            return palabra

    # Prioridad 2: si contiene algún nombre dentro
    for nombre in nombres_validos:
        if nombre in email_user:
            return nombre

    return "Nombre no detectado"

# Descarga de plantilla CSV
st.markdown("### 🧾 Plantilla CSV de ejemplo")
st.markdown("Puedes descargar una plantilla para adaptar tu base de datos:")
plantilla_df = pd.DataFrame({
    "email": ["ejemplo1@gmail.com", "ejemplo2@hotmail.com"],
    "nombre": ["ana", ""]  # segunda fila sin nombre para demostrar que puede ir vacío
})
plantilla_csv = plantilla_df.to_csv(index=False)
st.download_button("📥 Descargar plantilla CSV", plantilla_csv, file_name="plantilla_genero.csv", mime="text/csv")

# Instrucciones antes del uploader
st.markdown("""
**Instrucciones importantes:**
- El archivo debe tener una columna llamada `email`.
- La columna `nombre` es opcional. Si no tienes el nombre, **déjalo en blanco** y el sistema lo detectará desde el correo electrónico.
""")


# Subida de archivo
archivo = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if archivo:
    try:
        df = pd.read_csv(archivo, encoding="utf-8", sep=";", on_bad_lines="skip")
        df.columns = df.columns.str.strip().str.lower()

        if "email" not in df.columns:
            st.error("❌ El archivo debe tener una columna llamada 'email'")
            st.stop()

        # Limpieza y homogenización
        df["email"] = df["email"].astype(str).str.strip().str.lower()
        if "nombre" in df.columns:
            df["nombre_original"] = df["nombre"].fillna("").astype(str).str.strip().str.lower()
        else:
            df["nombre_original"] = ""

        # Nombre detectado solo si campo nombre está vacío
        df["nombre_detectado"] = df.apply(
            lambda row: row["nombre_original"] if row["nombre_original"] != "" else extraer_nombre_desde_email(row["email"]),
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

        # Resultados
        st.success("✅ Resultado del análisis")
        st.dataframe(df_final[["email", "nombre_detectado", "fuente_nombre", "gender"]])

        # Gráfico resumen
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
