import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="DTF Alpha Cleaner Pro", layout="wide")

# ✅ CSS compatible con todas las versiones de Streamlit
st.markdown("""
<style>
.black-box {
    background-color: #000000;
    padding: 15px;
    border-radius: 8px;
    border: 1px solid #444;
    text-align: center;
    margin-bottom: 10px;
}
.black-box img {
    background-color: #000000 !important;
    display: block;
    margin: 0 auto;
}
</style>
""", unsafe_allow_html=True)

if 'key' not in st.session_state:
    st.session_state.key = 0

def restart():
    st.session_state.key += 1
    # ✅ Compatibilidad máxima: usa experimental_rerun para versiones antiguas
    st.experimental_rerun()

st.title("DTF Alpha Cleaner Pro")
st.write("Limpia bordes suaves de IA para una impresión DTF perfecta.")

uploaded_file = st.file_uploader(
    "Sube tu diseño (PNG con transparencia)", 
    type=["png"], 
    key="uploader_" + str(st.session_state.key)
)

if uploaded_file is not None:
    with st.sidebar:
        st.header("Ajustes")
        threshold = st.slider(
            "Umbral de limpieza", 
            0, 
            255, 
            128,
            help="Valores por debajo de este umbral se eliminarán"
        )
        
        st.info("Rojo = Areas a eliminar | Negro = Transparente | Colores = Conservados")
        
        if st.button("Cargar otra imagen"):
            restart()

    img = Image.open(uploaded_file).convert("RGBA")
    pixels = list(img.getdata())
    preview_pixels = []
    clean_pixels = []
    
    for p in pixels:
        r, g, b, a = p
        if 0 < a < threshold:
            preview_pixels.append((255, 0, 0, 255))
            clean_pixels.append((0, 0, 0, 0))
        elif a == 0:
            preview_pixels.append((0, 0, 0, 0))
            clean_pixels.append((0, 0, 0, 0))
        else:
            preview_pixels.append((r, g, b, 255))
            clean_pixels.append((r, g, b, 255))

    img_preview = Image.new("RGBA", img.size)
    img_preview.putdata(preview_pixels)
    
    img_clean = Image.new("RGBA", img.size)
    img_clean.putdata(clean_pixels)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. ORIGINAL")
        st.image(img, width=300)

    with col2:
        st.subheader("2. RESULTADO (FONDO NEGRO)")
        st.markdown('<div class="black-box">', unsafe_allow_html=True)
        st.image(img_preview, width=300)
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("ROJO = Areas eliminadas")

    st.markdown("---")
    
    buf = io.BytesIO()
    img_clean.save(buf, format="PNG")
    
    st.download_button(
        label="DESCARGAR PNG LIMPIO",
        data=buf.getvalue(),
        file_name="dtf_limpio.png",
        mime="image/png"
    )
    
    st.success("Imagen lista para impresión DTF")

else:
    st.info("""
    **Instrucciones:**
    1. Sube un PNG con transparencia
    2. Ajusta el umbral según tus necesidades
    3. Descarga el resultado
    
    *Umbral recomendado:*
    - Sombras suaves: 50-80
    - Bordes definidos: 150+
    """)
