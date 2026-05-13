import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="DTF Alpha Cleaner Pro", layout="wide")

# Estilo para el fondo negro del resultado (muy simple para evitar errores)
st.markdown("""
    <style>
    .black-box {
        background-color: #000000;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #444;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

if 'key' not in st.session_state:
    st.session_state.key = 0

def restart():
    st.session_state.key += 1
    st.rerun()

st.title("🧼 DTF Alpha Cleaner Pro")
st.write("Limpia bordes suaves de IA para una impresión DTF perfecta.")

uploaded_file = st.file_uploader("Sube tu diseño (PNG con transparencia)", type=["png"], key=f"uploader_{st.session_state.key}")

if uploaded_file is not None:
    with st.sidebar:
        st.header("⚙️ Ajustes")
        threshold = st.slider("Umbral de limpieza", 0, 255, 128, 
                             help="Lo que esté por debajo de este valor se marcará en ROJO y se borrará.")
        
        st.divider()
        if st.button("🔄 Cargar otra imagen"):
            restart()

    img = Image.open(uploaded_file).convert("RGBA")
    
    # Usamos list() para ser compatibles con versiones viejas y nuevas de Pillow
    pixels = list(img.getdata())
    preview_pixels = [] # Con marcas rojas
    clean_pixels = []   # Para la descarga real
    
    for p in pixels:
        r, g, b, a = p
        if 0 < a < threshold:
            preview_pixels.append((255, 0, 0, 255)) # Rojo para el visor
            clean_pixels.append((0, 0, 0, 0))       # Transparente para descargar
        elif a == 0:
            preview_pixels.append((0, 0, 0, 0))
            clean_pixels.append((0, 0, 0, 0))
        else:
            # Si es sólido, lo dejamos sólido (255)
            preview_pixels.append((r, g, b, 255))   
            clean_pixels.append((r, g, b, 255))

    img_preview = Image.new("RGBA", img.size)
    img_preview.putdata(preview_pixels)
    
    img_clean = Image.new("RGBA", img.size)
    img_clean.putdata(clean_pixels)

    col1, col2 = st.columns(2)

    col1, col2 = st.columns(2)

with col1:
    st.subheader("🖼️ 1. ORIGINAL")
    st.image(img, use_container_width=True)

with col2:
    st.subheader("🔍 2. RESULTADO (FONDO NEGRO)")
    # ✅ CORREGIDO: Ahora muestra la imagen PROCESADA con bordes rojos
    st.markdown('<div class="black-box">', unsafe_allow_html=True)
    st.image(img_preview, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("""
    <style>
    .black-box img {
        background-color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)
    st.caption("Píxeles ROJOS = Semitransparencias que serán eliminadas.")

    st.divider()
    buf = io.BytesIO()
    img_clean.save(buf, format="PNG")
    
    st.download_button(
        label="💾 DESCARGAR PNG LIMPIO (Sin bordes rojos)",
        data=buf.getvalue(),
        file_name="dtf_limpio.png",
        mime="image/png"
    )
