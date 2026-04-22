import streamlit as st
import requests

st.title("TEST API")

TOKEN = st.secrets["API_CNE"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

resp = requests.get(
    "https://api.cne.cl/api/v4/estaciones",
    headers=headers
)

data = resp.json()

st.write(data)  # 👈 clave
