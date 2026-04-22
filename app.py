import streamlit as st
import requests
import math
import pandas as pd

st.set_page_config(page_title="Bencinas Pro", layout="wide")

st.title("🚗 Encuentra la bencina más conveniente")

TOKEN = st.secrets["API_CNE"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# 🔽 inputs
col1, col2 = st.columns(2)

with col1:
    ciudad = st.selectbox(
        "Ciudad",
        ["Osorno", "Puerto Montt", "Valdivia", "Santiago"]
    )

    tipo_bencina = st.selectbox(
        "Tipo de bencina",
        ["93", "95", "97"]
    )

with col2:
    lat_usuario = st.number_input("Tu latitud", value=-40.573)
    lon_usuario = st.number_input("Tu longitud", value=-73.133)

# 🔧 limpiar texto
def limpiar(texto):
    texto = str(texto).lower().strip()
    return (
        texto.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

# 📏 distancia Haversine
def distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

if st.button("Buscar"):

    url = "https://api.cne.cl/api/v4/estaciones?offset=0"
    resp = requests.get(url, headers=headers)

    if resp.status_code == 200:

        data = resp.json()

        if isinstance(data, dict):
            estaciones = data.get("data", [])
        else:
            estaciones = data

        ciudad_clean = limpiar(ciudad)
        resultados = []

        for est in estaciones:

            ubicacion = est.get("ubicacion", {})

            comuna = limpiar(ubicacion.get("nombre_comuna", ""))
            direccion = ubicacion.get("direccion", "")

            if ciudad_clean in comuna:

                marca = est.get("distribuidor", {}).get("marca", "Sin marca")

                precios = est.get("precios", {})
                precio = precios.get(tipo_bencina, {}).get("precio")

                lat = float(ubicacion.get("latitud", 0))
                lon = float(ubicacion.get("longitud", 0))

                if precio:
                    dist = distancia(lat_usuario, lon_usuario, lat, lon)

                    resultados.append({
                        "marca": marca,
                        "direccion": direccion,
                        "precio": float(precio),
                        "lat": lat,
                        "lon": lon,
                        "distancia": dist
                    })

        # 🔥 orden inteligente
        resultados = sorted(resultados, key=lambda x: (x["precio"], x["distancia"]))

        if resultados:

            st.subheader("⛽ Mejores opciones")

            # 🔽 tabla + mapa
            df = pd.DataFrame(resultados)

            # Mostrar top
            for r in resultados[:10]:
                st.markdown(
                    f"""
                    ### ⛽ {r['marca']}
                    📍 {r['direccion']}  
                    💰 **${int(r['precio'])}**  
                    📏 {round(r['distancia'],2)} km
                    ---
                    """
                )

            # 🔥 MAPA
            st.subheader("🗺️ Mapa")
            st.map(df[["lat", "lon"]])

        else:
            st.warning("No se encontraron estaciones")

    else:
        st.error("Error con la API")
