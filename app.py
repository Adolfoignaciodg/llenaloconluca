import streamlit as st
import requests
import math

st.title("🚗 Buscador de bencinas")

TOKEN = st.secrets["API_CNE"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# 🏙️ ciudades predefinidas
ciudades = {
    "Osorno": (-40.574, -73.133),
    "Puerto Montt": (-41.469, -72.942),
    "Valdivia": (-39.814, -73.245),
    "Santiago": (-33.448, -70.669)
}

ciudad = st.selectbox("Selecciona tu ciudad", list(ciudades.keys()))

lat_usuario, lon_usuario = ciudades[ciudad]

# 📏 distancia
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

# 🎚️ radio
radio = st.slider("Radio de búsqueda (km)", 5, 100, 30)

if st.button("Buscar estaciones"):

    response = requests.get(
        "https://api.cne.cl/api/v4/estaciones",
        headers=headers
    )

    if response.status_code == 200:

        data = response.json()
        resultados = []

        for est in data:

            lat_est = est.get("latitud")
            lon_est = est.get("longitud")

            if not lat_est or not lon_est:
                continue

            try:
                dist = calcular_distancia(
                    lat_usuario,
                    lon_usuario,
                    float(lat_est),
                    float(lon_est)
                )
            except:
                continue

            if dist <= radio:

                nombre = est.get("razon_social", "Sin nombre")
                direccion = est.get("direccion_calle", "")
                comuna = est.get("comuna", "")

                resultados.append({
                    "nombre": nombre,
                    "direccion": direccion,
                    "comuna": comuna,
                    "distancia": round(dist, 2)
                })

        resultados = sorted(resultados, key=lambda x: x["distancia"])

        if resultados:
            st.subheader("⛽ Estaciones cercanas")

            for r in resultados[:10]:
                st.write(
                    f"**{r['nombre']}**  \n"
                    f"{r['direccion']} - {r['comuna']}  \n"
                    f"📍 {r['distancia']} km"
                )
        else:
            st.warning("No se encontraron estaciones cercanas")

    else:
        st.error("Error con la API")
