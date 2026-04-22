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

# 🔽 función limpiar texto
def limpiar(texto):
    texto = str(texto).lower().strip()
    return (
        texto.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )

# 📏 distancia
def distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

# 🔽 traer estaciones (solo 1 vez)
@st.cache_data
def cargar_estaciones():
    resp = requests.get("https://api.cne.cl/api/v4/estaciones?offset=0", headers=headers)
    data = resp.json()

    if isinstance(data, dict):
        return data.get("data", [])
    return data

estaciones = cargar_estaciones()

# 🔥 obtener comunas dinámicas
comunas = sorted(list(set([
    est.get("ubicacion", {}).get("nombre_comuna")
    for est in estaciones
    if est.get("ubicacion", {}).get("nombre_comuna")
])))

# 🔽 inputs
col1, col2 = st.columns(2)

with col1:
    ciudad = st.selectbox("Selecciona tu comuna", comunas)
    tipo_bencina = st.selectbox("Tipo de bencina", ["93", "95", "97"])

# 🔥 usar coordenadas promedio de la comuna
def obtener_coordenadas_comuna(nombre_comuna):
    coords = [
        (
            float(est.get("ubicacion", {}).get("latitud", 0)),
            float(est.get("ubicacion", {}).get("longitud", 0))
        )
        for est in estaciones
        if est.get("ubicacion", {}).get("nombre_comuna") == nombre_comuna
    ]

    if coords:
        lat_prom = sum(c[0] for c in coords) / len(coords)
        lon_prom = sum(c[1] for c in coords) / len(coords)
        return lat_prom, lon_prom

    return 0, 0

lat_usuario, lon_usuario = obtener_coordenadas_comuna(ciudad)

st.write(f"📍 Ubicación estimada: {ciudad}")

# 🔽 buscar
if st.button("Buscar"):

    ciudad_clean = limpiar(ciudad)
    resultados = []

    for est in estaciones:

        ubicacion = est.get("ubicacion", {})
        comuna = limpiar(ubicacion.get("nombre_comuna", ""))

        if ciudad_clean == comuna:

            marca = est.get("distribuidor", {}).get("marca", "Sin marca")
            direccion = ubicacion.get("direccion", "")

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

    resultados = sorted(resultados, key=lambda x: (x["precio"], x["distancia"]))

    if resultados:

        st.subheader("⛽ Mejores opciones")

        df = pd.DataFrame(resultados)

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

        st.subheader("🗺️ Mapa")
        st.map(df[["lat", "lon"]])

    else:
        st.warning("No se encontraron estaciones")
