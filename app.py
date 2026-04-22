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

# 🔧 función para limpiar texto
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

        # 🔥 manejar formatos de respuesta
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

            comuna_raw = est.get("comuna", "")
            comuna = limpiar(comuna_raw)

            # 🔥 filtro robusto
            if ciudad_clean in comuna:

                nombre = est.get("razon_social", "Sin nombre")
                direccion = est.get("direccion_calle", "")
                comuna_real = est.get("comuna", "")

                resultados.append({
                    "nombre": nombre,
                    "direccion": direccion,
                    "comuna": comuna_real
                })

        if resultados:
            st.subheader("⛽ Estaciones encontradas")

            for r in resultados[:20]:
                st.write(
                    f"**{r['nombre']}**  \n"
                    f"{r['direccion']} - {r['comuna']}"
                )
        else:
            st.warning("No se encontraron estaciones con ese filtro")

            # 🧪 DEBUG: mostrar comunas reales
            st.subheader("🔍 Debug comunas disponibles")
            comunas = list(set([est.get("comuna") for est in estaciones if est.get("comuna")]))
            st.write(comunas[:50])

    else:
        st.error("Error con la API")
        st.write(resp.text)
