import streamlit as st
import requests

st.title("🚗 Buscador de bencinas")

# 🔑 token desde Streamlit
TOKEN = st.secrets["API_CNE"]

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# 🏙️ selector de ciudad
ciudad = st.selectbox(
    "Selecciona tu ciudad",
    ["Osorno", "Puerto Montt", "Valdivia", "Santiago"]
)

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
        precios = precio_resp.json().get("data", [])

        # 🔍 función mejorada para encontrar precio
        def obtener_precio(region, tipo="93"):

            region = str(region).lower()

            for p in precios:

                region_api = str(p.get("region", "")).lower()
                combustible_api = str(p.get("combustible", "")).lower()

                if region in region_api and tipo in combustible_api:
                    return p.get("precio")

            return None

        resultados = []

        for est in estaciones:

            comuna_api = str(est.get("comuna", "")).lower()

            # 🔥 filtro más flexible
            if ciudad.lower() in comuna_api or comuna_api in ciudad.lower():

                nombre = est.get("razon_social", "Sin nombre")
                direccion = est.get("direccion_calle", "")
                comuna = est.get("comuna", "")
                region = est.get("region", "")

                precio = obtener_precio(region)

                if precio is not None:
                    resultados.append({
                        "nombre": nombre,
                        "direccion": direccion,
                        "precio": precio
                    })

        # ordenar por precio
        resultados = sorted(resultados, key=lambda x: x["precio"])

        # mostrar resultados
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

# 🧪 DEBUG opcional (puedes borrar después)
# st.write(precios[:5])
