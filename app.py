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
        else:
            estaciones = json_data

        st.write(f"Total estaciones: {len(estaciones)}")

        resultados = []
        ciudad_clean = limpiar(ciudad)

        for est in estaciones:

            ubicacion = est.get("ubicacion", {})

            comuna = limpiar(ubicacion.get("nombre_comuna", ""))
            direccion = ubicacion.get("direccion", "")

            if ciudad_clean in comuna:

                nombre = est.get("razon_social", "Sin nombre")

                # 💰 precios reales por estación 🔥
                precios = est.get("precios", {})
                precio_93 = precios.get("93", {}).get("precio")

                resultados.append({
                    "nombre": nombre,
                    "direccion": direccion,
                    "precio": precio_93
                })

        # ordenar por precio si existe
        resultados = [r for r in resultados if r["precio"] is not None]
        resultados = sorted(resultados, key=lambda x: float(x["precio"]))

        if resultados:
            st.subheader("⛽ Mejores opciones (Gasolina 93)")

            for r in resultados[:15]:
                st.write(
                    f"**{r['nombre']}**  \n"
                    f"{r['direccion']}  \n"
                    f"💰 ${r['precio']}"
                )
        else:
            st.warning("No se encontraron estaciones en esa ciudad")

    else:
        st.error("Error con la API")
        st.write(resp.text)
