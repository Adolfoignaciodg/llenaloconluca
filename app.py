import streamlit as st
import requests

st.title("🚗 Buscador de bencinas")

TOKEN = st.secrets["API_CNE"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# 🏙️ seleccionar ciudad
ciudad = st.selectbox("Selecciona tu ciudad", ["Osorno", "Puerto Montt", "Valdivia", "Santiago"])

if st.button("Buscar estaciones"):

    # 🔽 estaciones
    est_resp = requests.get(
        "https://api.cne.cl/api/v4/estaciones",
        headers=headers
    )

    # 🔽 precios
    precio_resp = requests.get(
        "https://api.cne.cl/api/ea/precio/combustibleliquido",
        headers=headers
    )

    if est_resp.status_code == 200 and precio_resp.status_code == 200:

        estaciones = est_resp.json()
        precios = precio_resp.json()["data"]

        # 🔍 función para buscar precio
        def obtener_precio(region, tipo="Gasolina 93"):
            for p in precios:
                if p["region"] == region and tipo in p["combustible"]:
                    return p["precio"]
            return None

        resultados = []

        for est in estaciones:

            comuna_api = est.get("comuna", "").lower()

            if ciudad.lower() in comuna_api:

                nombre = est.get("razon_social", "Sin nombre")
                direccion = est.get("direccion_calle", "")
                comuna = est.get("comuna", "")
                region = est.get("region")

                precio = obtener_precio(region)

                resultados.append({
                    "nombre": nombre,
                    "direccion": direccion,
                    "precio": precio
                })

        # ordenar por precio
        resultados = [r for r in resultados if r["precio"] is not None]
        resultados = sorted(resultados, key=lambda x: x["precio"])

        # mostrar
        if resultados:
            st.subheader("⛽ Mejores opciones")

            for r in resultados[:10]:
                st.write(
                    f"**{r['nombre']}**  \n"
                    f"{r['direccion']}  \n"
                    f"💰 ${r['precio']}"
                )
        else:
            st.warning("No se encontraron datos")

    else:
        st.error("Error con la API")
