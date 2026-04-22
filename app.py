import streamlit as st
import requests

st.set_page_config(page_title="Buscador de Bencinas", layout="wide")

st.title("🚗 Encuentra la bencina más barata")

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
                precio_93 = precios.get("93", {}).get("precio")

                if precio_93:
                    resultados.append({
                        "marca": marca,
                        "direccion": direccion,
                        "precio": float(precio_93)
                    })

        resultados = sorted(resultados, key=lambda x: x["precio"])

        if resultados:

            st.subheader("⛽ Mejores precios en tu ciudad")

            for r in resultados[:15]:
                st.markdown(
                    f"""
                    ### ⛽ {r['marca']}
                    📍 {r['direccion']}  
                    💰 **${int(r['precio'])}**
                    ---
                    """
                )

        else:
            st.warning("No se encontraron estaciones")

    else:
        st.error("Error con la API")
