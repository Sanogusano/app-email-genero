import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from PIL import Image

st.set_page_config(page_title="Género Match", layout="centered", page_icon="👤")
st.markdown("<style>body {background-color: #fdcf2d;}</style>", unsafe_allow_html=True)

# Logo
logo = Image.open("logo.jpg")
st.image(logo, width=250)

# Instrucciones
st.markdown("""
# 👤 Clasificador de Género por Nombre

📂 **Instrucciones:**  
- El archivo debe tener las columnas `email`, `nombre`.  
- Si no hay `nombre`, se intentará extraer desde el correo.  
- Solo válido para nombres en Latinoamérica.  

---
""")

@st.cache_data
def cargar_diccionario():
    df = pd.read_csv("latam_forenames.csv")
    df = df.drop_duplicates(subset="forename")
    df["forename"] = df["forename"].str.lower().str.strip()
    return df[["forename", "gender"]]

diccionario = cargar_diccionario()

archivo = st.file_uploader("📤 Sube tu archivo CSV", type=["csv"])

if archivo:
    try:
        df = pd.read_csv(archivo, encoding="utf-8", sep=";", on_bad_lines="skip")
        df.columns = df.columns.str.strip().str.lower()

        if "email" not in df.columns:
            st.error("❌ El archivo debe tener una columna llamada 'email'.")
            st.stop()

        # Extraer nombre original si existe
        df["nombre_original"] = df["nombre"] if "nombre" in df.columns else ""

        # Si no hay nombre o está vacío, intentar extraer desde email
        def extraer_nombre(email):
            email = str(email).split("@")[0]
            match = re.split(r"[._\-]", email)
            if match and re.match(r"^[a-záéíóúüñ]{3,}$", match[0], re.IGNORECASE):
                return match[0]
            return "Nombre no detectado"

        df["nombre_detectado"] = df.apply(
            lambda row: row["nombre_original"] if pd.notnull(row["nombre_original"]) and row["nombre_original"].strip() != ""
            else extraer_nombre(row["email"]), axis=1
        )

        # Limpiar nombres
        df["nombre_limpio"] = df["nombre_detectado"].str.lower().str.strip()
        df["nombre_limpio"] = df["nombre_limpio"].str.replace(r"[^a-záéíóúüñ ]", "", regex=True)

        # Match con diccionario
        df_genero = df.merge(diccionario, how="left", left_on="nombre_limpio", right_on="forename")
        df_genero["gender"] = df_genero["gender"].fillna("No identificado")

        # Mostrar resultado
        st.success("✅ Resultado del análisis")
        st.dataframe(df_genero[["email", "nombre_original", "nombre_detectado", "gender"]])

        # Gráfico resumen
        genero_counts = df_genero["gender"].value_counts()
        fig, ax = plt.subplots()
        genero_counts.plot(kind='bar', ax=ax, color='mediumslateblue')
        ax.set_title("Distribución de Géneros Detectados")
        ax.set_xlabel("Género")
        ax.set_ylabel("Cantidad")
        st.pyplot(fig)

        # Descargar resultados
        csv_final = df_genero[["email", "nombre_original", "nombre_detectado", "gender"]].to_csv(index=False)
        st.download_button("📥 Descargar resultados", csv_final, file_name="genero_detectado.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")

# Footer
st.markdown("---")
st.markdown("Copyright © 2025 - Andrés Restrepo  |  [LinkedIn](https://www.linkedin.com/in/andresrestrepoh/)")
