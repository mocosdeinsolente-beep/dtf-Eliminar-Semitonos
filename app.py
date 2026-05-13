import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="DTF Alpha Cleaner", layout="centered")

st.title("🧼 DTF Alpha Cleaner")
st.write("Elimina semitransparencias y bordes suaves de imágenes generadas por IA.")

# Subida de archivo
uploaded_file = st.file_uploader("Sube tu diseño (PNG con transparencia)", type=["png"])

if uploaded_file is not None:
    # Cargar imagen
    img = Image.open(uploaded_file).convert("RGBA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(img, caption="Imagen Original", use_container_width=True)

    # Configuración del umbral
    # 128 es el punto medio (50% de opacidad)
    threshold = st.slider("Umbral de opacidad (Threshold)", 0, 255, 128, 
                          help="Píxeles con opacidad menor a este valor serán eliminados. Los mayores serán 100% sólidos.")

    # Procesamiento
    data = img.getdata()
    new_data = []
    
    for item in data:
        # item[3] es el canal alfa
        if item[3] < threshold:
            new_data.append((0, 0, 0, 0)) # Transparente total
        else:
            new_data.append((item[0], item[1], item[2], 255)) # Opaco total

    img.putdata(new_data)

    with col2:
        st.image(img, caption="Resultado para DTF", use_container_width=True)

    # Botón de descarga
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Descargar PNG limpio",
        data=byte_im,
        file_name="diseno_limpio_dtf.png",
        mime="image/png"
    )
