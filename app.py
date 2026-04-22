import streamlit as st
import requests
import math

st.title("🚗 Buscador de bencinas")

# 🔑 token desde Streamlit Cloud
TOKEN = st.secrets["API_CNE"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# 📍 inputs
lat_usuario = st.number_input("Latitud", value=-40.574)
lon_usuario = st.number_input("Longitud", value=-73.133)

# 📏 función distancia
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


# 🔘 botón
if st.button("Buscar estaciones cercanas"):

    response = requests.get(
        "https://api.cne.cl/api/v4/estaciones",
        headers=headers
    )

    if response.status_code == 200:

        data = response.json()

        st.success("Conexión OK ✅")

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

            # filtrar cercanas (10 km)
            if dist <= 10:

                nombre = est.get("razon_social", "Sin nombre")
                direccion = est.get("direccion_calle", "")
                comuna = est.get("comuna", "")

                resultados.append({
                    "nombre": nombre,
                    "direccion": direccion,
                    "comuna": comuna,
                    "distancia": round(dist, 2)
                })

        # ordenar por distancia
        resultados = sorted(resultados, key=lambda x: x["distancia"])

        # mostrar resultados
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
        st.error("Error con la API ❌")
        st.write(response.text)
