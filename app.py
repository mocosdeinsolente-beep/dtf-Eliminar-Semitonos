import streamlit as st
from PIL import Image, ImageOps
import io

st.set_page_config(page_title="DTF Alpha Cleaner Pro", layout="wide")

# Inicializar estado para el reinicio (para que el botón de volver funcione)
if 'uploaded_file_id' not in st.session_state:
    st.session_state.uploaded_file_id = 0

def reset_app():
    st.session_state.uploaded_file_id += 1
    st.rerun()

st.title("🧼 DTF Alpha Cleaner Pro")
st.write("Detecta semitonos problemáticos y prepara tus archivos para DTF.")

with st.sidebar:
    st.header("Configuración")
    threshold = st.slider("Umbral de opacidad (Threshold)", 0, 255, 128, 
                          help="Píxeles con opacidad menor a esto se borran. Mayores se vuelven sólidos.")
    
    zoom_factor = st.slider("Zoom Digital (%)", 100, 500, 100, help="Aumenta para ver los bordes de cerca.")
    
    if st.button("🔄 Reiniciar / Nueva Imagen"):
        reset_app()

uploaded = st.file_uploader("Sube tu archivo PNG", type=["png"], key=f"uploader_{st.session_state.uploaded_file_id}")

if uploaded:
    img_orig = Image.open(uploaded).convert("RGBA")
    width, height = img_orig.size
    
    data = img_orig.getdata()
    
    # 1. Imagen Limpia (Resultado)
    new_data_clean = []
    # 2. Mapa de Semitonos (Rojo)
    new_data_red = []
    
    for item in data:
        # item[3] es el canal alfa (transparencia)
        if item[3] == 0:
            new_data_clean.append((0, 0, 0, 0))
            new_data_red.append((0, 0, 0, 0))
        elif item[3] < threshold:
            # Semitono detectado que se va a borrar -> Marcamos en rojo
            new_data_clean.append((0, 0, 0, 0))
            new_data_red.append((255, 0, 0, 255)) 
        elif item[3] < 255:
            # Semitono detectado que se hará sólido -> Marcamos en rojo
            new_data_clean.append((item[0], item[1], item[2], 255))
            new_data_red.append((255, 0, 0, 255))
        else:
            # Píxel ya sólido (perfecto para DTF)
            new_data_clean.append((item[0], item[1], item[2], 255))
            new_data_red.append((item[0], item[1], item[2], 255))

    img_clean = Image.new("RGBA", img_orig.size)
    img_clean.putdata(new_data_clean)
    
    img_red = Image.new("RGBA", img_orig.size)
    img_red.putdata(new_data_red)

    if zoom_factor > 100:
        new_w, new_h = int(width * 100 / zoom_factor), int(height * 100 / zoom_factor)
        left = (width - new_w) / 2
        top = (height - new_h) / 2
        right = (width + new_w) / 2
        bottom = (height + new_h) / 2
        
        view_orig = img_orig.crop((left, top, right, bottom))
        view_red = img_red.crop((left, top, right, bottom))
        view_clean = img_clean.crop((left, top, right, bottom))
    else:
        view_orig, view_red, view_clean = img_orig, img_red, img_clean

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1. Original")
        st.image(view_orig, use_container_width=True)
        
    with col2:
        st.subheader("2. Semitonos (Rojo)")
        st.image(view_red, use_container_width=True)
        st.caption("Los píxeles rojos son los que tienen transparencia y darán problemas.")

    with col3:
        st.subheader("3. Resultado Final")
        st.image(view_clean, use_container_width=True)

    st.divider()
    buf = io.BytesIO()
    img_clean.save(buf, format="PNG")
    
    col_dl1, col_dl2 = st.columns([1, 1])
    with col_dl1:
        st.download_button(
            label="💾 Descargar PNG para DTF",
            data=buf.getvalue(),
            file_name="limpio_para_dtf.png",
            mime="image/png",
            use_container_width=True
        )
    with col_dl2:
        if st.button("🔙 Cargar otra imagen", use_container_width=True):
            reset_app()
