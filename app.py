import streamlit as st
import requests

st.title("🚗 Bencinas por ciudad")

TOKEN = st.secrets["API_CNE"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# selector ciudad
ciudad = st.selectbox(
    "Selecciona tu ciudad",
    ["Osorno", "Puerto Montt", "Valdivia", "Santiago"]
)

if st.button("Buscar"):

    # 🔥 IMPORTANTE: offset=0
    url = "https://api.cne.cl/api/v4/estaciones?offset=0"

    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:

        json_data = resp.json()

        # 🔥 CLAVE: entrar a "data"
        estaciones = json_data.get("data", [])

        st.write(f"Total estaciones recibidas: {len(estaciones)}")

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
            st.warning("No se encontraron estaciones en esta página (offset=0)")

    else:
        st.error("Error con la API")
        st.write(resp.text)
