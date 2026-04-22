import streamlit as st
import requests

st.title("🚗 Buscador de bencinas")

# 🔑 token desde Streamlit Cloud
TOKEN = st.secrets["API_CNE"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# botón
if st.button("Buscar estaciones"):

    response = requests.get(
        "https://api.cne.cl/api/v4/estaciones",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()

        st.success("Conexión OK ✅")

        # mostrar primeras 5 estaciones
        for est in data[:5]:
            st.write(est["nombre"])

    else:
        st.error("Error con la API ❌")
        st.write(response.text)
