import streamlit as st
import requests
import math
import pandas as pd

st.set_page_config(page_title="Bencinas Pro", layout="wide")
st.title("🚗 Encuentra la bencina más conveniente")

TOKEN = st.secrets["API_CNE"]

headers = {"Authorization": f"Bearer {TOKEN}"}


# -------------------------
# UTILIDADES
# -------------------------

def limpiar(texto):
    if not texto:
        return ""
    texto = str(texto).lower().strip()
    return (
        texto.replace("á", "a")
        .replace("é", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ú", "u")
    )


def distancia(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# -------------------------
# CARGA DE DATOS (PAGINADO)
# -------------------------

@st.cache_data
def cargar_estaciones():
    estaciones = []
    offset = 0
    limit = 500

    while True:
        url = f"https://api.cne.cl/api/v4/estaciones?offset={offset}"
        resp = requests.get(url, headers=headers)

        if resp.status_code != 200:
            break

        data = resp.json().get("data", [])
        if not data:
            break

        estaciones.extend(data)
        offset += limit

    return estaciones


estaciones = cargar_estaciones()


# -------------------------
# REGIONES / COMUNAS
# -------------------------

regiones = sorted(list(set([
    est.get("ubicacion", {}).get("nombre_region")
    for est in estaciones
    if est.get("ubicacion", {}).get("nombre_region")
])))

col1, col2 = st.columns(2)

with col1:
    region = st.selectbox("Región", regiones)

    comunas = sorted(list(set([
        est.get("ubicacion", {}).get("nombre_comuna")
        for est in estaciones
        if est.get("ubicacion", {}).get("nombre_region") == region
    ])))

    comuna = st.selectbox("Comuna", comunas)

with col2:
    tipo_bencina = st.selectbox("Tipo de bencina", ["93", "95", "97"])


# -------------------------
# CENTRO COMUNA (APPROX)
# -------------------------

def centro_comuna(nombre_comuna):
    coords = [
        (
            float(e.get("ubicacion", {}).get("latitud", 0)),
            float(e.get("ubicacion", {}).get("longitud", 0)),
        )
        for e in estaciones
        if e.get("ubicacion", {}).get("nombre_comuna") == nombre_comuna
    ]

    if not coords:
        return 0, 0

    return (
        sum(c[0] for c in coords) / len(coords),
        sum(c[1] for c in coords) / len(coords),
    )


lat_user, lon_user = centro_comuna(comuna)

st.write(f"📍 Ubicación estimada: {comuna}")


# -------------------------
# BUSQUEDA
# -------------------------

if st.button("Buscar"):

    resultados = []

    for est in estaciones:

        ubicacion = est.get("ubicacion", {})
        if ubicacion.get("nombre_comuna") != comuna:
            continue

        precios = est.get("precios", {})
        precio = precios.get(tipo_bencina, {}).get("precio")

        if not precio:
            continue

        lat = float(ubicacion.get("latitud", 0))
        lon = float(ubicacion.get("longitud", 0))

        dist = distancia(lat_user, lon_user, lat, lon)

        resultados.append({
            "marca": est.get("distribuidor", {}).get("marca", "Sin marca"),
            "direccion": ubicacion.get("direccion", ""),
            "precio": float(precio),
            "lat": lat,
            "lon": lon,
            "distancia": dist
        })

    resultados.sort(key=lambda x: (x["precio"], x["distancia"]))

    if resultados:

        st.subheader("⛽ Mejores opciones")

        df = pd.DataFrame(resultados)

        for r in resultados[:10]:
            st.markdown(
                f"""
                ### ⛽ {r['marca']}
                📍 {r['direccion']}  
                💰 **${int(r['precio'])}**  
                📏 {round(r['distancia'], 2)} km  
                ---
                """
            )

        st.subheader("🗺️ Mapa")
        st.map(df[["lat", "lon"]])

    else:
        st.warning("No se encontraron estaciones")
