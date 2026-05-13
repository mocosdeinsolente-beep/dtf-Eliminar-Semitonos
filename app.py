import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="Limpiador DTF Pro", layout="wide")

st.markdown("""
    <style>
    /* Fondo negro solo para el área de la imagen de resultado */
    .black-bg {
        background-color: #000000;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #444;
        text-align: center;
    }
    .stButton>button { width: 100%; }
    .stDownloadButton>button { width: 100%; background-color: #28a745; color: white; }
    </style>
    """, unsafe_allow_html=True)

def restart():
    if 'file' in st.session_state:
        del st.session_state.file
    st.rerun()

st.title("🧼 Limpiador de Semitonos DTF")

if 'file' not in st.session_state:
    uploaded = st.file_uploader("Sube tu archivo PNG con transparencia", type=["png"])
    if uploaded:
        st.session_state.file = uploaded
        st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ Configuración")
        threshold = st.slider("Umbral de Limpieza (Alpha)", 0, 255, 128, 
                             help="Lo que esté por debajo de este valor se marcará en ROJO y se eliminará.")
        
        st.divider()
        st.header("🔍 Visualización")
        zoom = st.slider("Zoom (Enfoque Central)", 1, 10, 1)
        
        st.divider()
        if st.button("🔄 Cargar otra imagen"):
            restart()

    img = Image.open(st.session_state.file).convert("RGBA")
    
    pixels = list(img.getdata())
    preview_pixels = []
    final_pixels = []
    
    for p in pixels:
        r, g, b, a = p
        if 0 < a < threshold:
            preview_pixels.append((255, 0, 0, 255)) # Rojo para el visor
            final_pixels.append((0, 0, 0, 0))       # Transparente para descargar
        elif a == 0:
            preview_pixels.append((0, 0, 0, 0))
            final_pixels.append((0, 0, 0, 0))
        else:
            preview_pixels.append((r, g, b, 255))   # Sólido
            final_pixels.append((r, g, b, 255))

    img_preview = Image.new("RGBA", img.size)
    img_preview.putdata(preview_pixels)
    
    img_final = Image.new("RGBA", img.size)
    img_final.putdata(final_pixels)

    if zoom > 1:
        w, h = img.size
        left = (w - w/zoom)/2
        top = (h - h/zoom)/2
        right = (w + w/zoom)/2
        bottom = (h + h/zoom)/2
        img_display_orig = img.crop((left, top, right, bottom))
        img_display_preview = img_preview.crop((left, top, right, bottom))
    else:
        img_display_orig = img
        img_display_preview = img_preview

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. ORIGINAL")
        st.image(img_display_orig, width='stretch')

    with col2:
        st.subheader("2. RESULTADO (Fondo Negro)")
        st.markdown('<div class="black-bg">', unsafe_allow_html=True)
        st.image(img_display_preview, width='stretch')
        st.markdown('</div>', unsafe_allow_html=True)
        st.info("Píxeles rojos = Semitransparencias que serán eliminadas")

    st.divider()
    dl_buffer = io.BytesIO()
    img_final.save(dl_buffer, format="PNG")
    
    st.download_button(
        label="💾 DESCARGAR PNG LIMPIO (SIN ROJO)",
        data=dl_buffer.getvalue(),
        file_name="dtf_limpio.png",
        mime="image/png"
    )
