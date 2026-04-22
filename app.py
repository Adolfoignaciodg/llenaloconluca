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

# limpiar texto
def limpiar(texto):
    texto = str(texto).lower().strip()
    return (
        texto.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

if st.button("Buscar"):

    url = "https://api.cne.cl/api/v4/estaciones?offset=0"
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:

        json_data = resp.json()

        if isinstance(json_data, dict):
            estaciones = json_data.get("data", [])
        elif isinstance(json_data, list):
            estaciones = json_data
        else:
            estaciones = []

        st.write(f"Total estaciones recibidas: {len(estaciones)}")

        resultados = []
        ciudad_clean = limpiar(ciudad)

        for est in estaciones:

            # 🔥 usar dirección completa
            direccion = f"{est.get('direccion_calle','')} {est.get('direccion_numero','')}"
            direccion_clean = limpiar(direccion)

            if ciudad_clean in direccion_clean:

                nombre = est.get("razon_social", "Sin nombre")

                resultados.append({
                    "nombre": nombre,
                    "direccion": direccion
                })

        if resultados:
            st.subheader("⛽ Estaciones encontradas")

            for r in resultados[:20]:
                st.write(f"**{r['nombre']}** - {r['direccion']}")
        else:
            st.warning("No se encontraron estaciones con ese filtro")

            # 🔥 DEBUG REAL
            st.subheader("🔍 Ejemplo de datos reales")
            st.write(estaciones[:3])

    else:
        st.error("Error con la API")
        st.write(resp.text)
