import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

st.set_page_config(page_title="Clasificador de Género por Nombre", layout="centered")
st.title("👤 Clasificador de Género por Nombre")

st.markdown("Sube un archivo .CSV con una columna llamada **Nombre**. El sistema asignará un género usando un diccionario de nombres.")

@st.cache_data
def cargar_diccionario():
    df = pd.read_csv("latam_forenames.csv", encoding="utf-8")
    df = df.drop_duplicates(subset="forename")
    df["forename"] = df["forename"].astype(str).str.strip().str.lower()
    df["gender"] = df["gender"].astype(str).str.strip()
    return df[["forename", "gender"]]

diccionario = cargar_diccionario()

archivo = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if archivo:
    try:
        df = pd.read_csv(archivo, encoding="utf-8", sep=";", on_bad_lines="skip")
        df.columns = df.columns.str.strip().str.lower()

        if "nombre" not in df.columns:
            st.error("❌ El archivo debe tener una columna llamada 'Nombre'")
            st.stop()

        df["nombre_limpio"] = df["nombre"].astype(str).str.lower().str.strip()
        df["nombre_limpio"] = df["nombre_limpio"].str.replace(r"[^a-záéíóúüñ ]", "", regex=True)

        df_genero = df.merge(diccionario, how="left", left_on="nombre_limpio", right_on="forename")
        df_genero["gender"] = df_genero["gender"].fillna("No identificado")

        st.success("✅ Resultado del análisis")
        st.dataframe(df_genero[["nombre", "gender"]])

        genero_counts = df_genero["gender"].value_counts()
        fig, ax = plt.subplots()
        genero_counts.plot(kind='bar', ax=ax, color='mediumslateblue')
        ax.set_title("Distribución de Géneros Detectados")
        ax.set_xlabel("Género")
        ax.set_ylabel("Cantidad")
        st.pyplot(fig)

        csv_final = df_genero[["nombre", "gender"]].to_csv(index=False)
        st.download_button("📥 Descargar resultados", csv_final, file_name="genero_detectado.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
