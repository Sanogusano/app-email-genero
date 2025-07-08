import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt
from PIL import Image

# 🎨 Estilos personalizados
st.set_page_config(page_title="Género Match", layout="centered")

page_bg_color = """
<style>
body {
    background-color: #fdcf2d;
}
[data-testid="stHeader"] {
    background: none;
}
[data-testid="stAppViewContainer"] {
    background-color: #fdcf2d;
}
</style>
"""
st.markdown(page_bg_color, unsafe_allow_html=True)

# 🖼️ Logo
try:
    logo = Image.open("logo.jpg")
    st.image(logo, width=250)
except:
    st.title("👤 Género Match")

# ✍️ Descripción
st.markdown("""
### Clasificador de Género por Nombre  
Sube un archivo `.CSV` con una columna llamada **Nombre**.  
El sistema asignará un género usando un diccionario confiable de nombres en español.
""")

# 📥 Cargar diccionario
@st.cache_data
def cargar_diccionario():
    df = pd.read_csv("latam_forenames.csv")
    df = df.drop_duplicates(subset="forename")
    df["forename"] = df["forename"].str.lower().str.strip()
    df["gender"] = df["gender"].str.upper().str.strip()
    return df[["forename", "gender"]]

diccionario = cargar_diccionario()

# 📂 Subida de archivo
archivo = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

# ⚙️ Procesamiento
if archivo:
    try:
        df = pd.read_csv(archivo, encoding="utf-8", sep=";", on_bad_lines="skip")
        df.columns = df.columns.str.strip().str.lower()

        if "nombre" not in df.columns:
            st.error("⚠️ El archivo debe tener una columna llamada 'Nombre'")
            st.stop()

        df["nombre_limpio"] = df["nombre"].str.lower().str.strip()
        df["nombre_limpio"] = df["nombre_limpio"].str.replace(r"[^a-záéíóúüñ ]", "", regex=True)
        df_genero = df.merge(diccionario, how="left", left_on="nombre_limpio", right_on="forename")
        df_genero["gender"] = df_genero["gender"].fillna("No identificado")

        # ✅ Resultados
        st.success("✅ Resultado del análisis")
        st.dataframe(df_genero[["nombre", "gender"]])

        # 📊 Gráfico
        genero_counts = df_genero["gender"].value_counts()
        fig, ax = plt.subplots()
        genero_counts.plot(kind='bar', ax=ax, color='mediumslateblue')
        ax.set_title("Distribución de Géneros Detectados")
        ax.set_xlabel("Género")
        ax.set_ylabel("Cantidad")
        st.pyplot(fig)

        # 📤 Botón descarga
        csv_final = df_genero[["nombre", "gender"]].to_csv(index=False)
        st.download_button("📥 Descargar resultados", csv_final, file_name="genero_detectado.csv", mime="text/csv")

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
