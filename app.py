import streamlit as st
import requests

st.title("🚗 Bencinas por ciudad")

TOKEN = st.secrets["API_CNE"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

ciudad = st.selectbox(
    "Selecciona tu ciudad",
    ["Osorno", "Puerto Montt", "Valdivia", "Santiago"]
)

if st.button("Buscar"):

    est_resp = requests.get(
        "https://api.cne.cl/api/v4/estaciones",
        headers=headers
    )

    if est_resp.status_code == 200:

        estaciones = est_resp.json()
        resultados = []

        for est in estaciones:

            comuna = str(est.get("comuna", "")).lower()

            if ciudad.lower() in comuna:

                nombre = est.get("razon_social", "Sin nombre")
                direccion = est.get("direccion_calle", "")

                resultados.append({
                    "nombre": nombre,
                    "direccion": direccion
                })

        if resultados:

            st.subheader("⛽ Estaciones encontradas")

            for r in resultados[:15]:
                st.write(f"**{r['nombre']}** - {r['direccion']}")

        else:
            st.warning("No se encontraron estaciones")

    else:
        st.error("Error con la API")
