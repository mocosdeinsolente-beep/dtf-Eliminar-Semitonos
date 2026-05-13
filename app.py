import streamlit as st
from PIL import Image
import io
import base64

# Configuración inicial
st.set_page_config(page_title="DTF Alpha Cleaner Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: transparent; }
    .result-container {
        background-color: #000000;
        border: 2px solid #444;
        border-radius: 8px;
        overflow: hidden;
        position: relative;
        height: 500px;
        width: 100%;
        cursor: grab;
    }
    .result-container:active { cursor: grabbing; }
    </style>
    """, unsafe_allow_html=True)

def reset_app():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

st.title("🧼 DTF Alpha Pro: Inspector de Bordes")

if 'uploaded_file' not in st.session_state:
    uploaded = st.file_uploader("Sube tu archivo PNG", type=["png"])
    if uploaded:
        st.session_state.uploaded_file = uploaded
        st.rerun()
else:
    with st.sidebar:
        st.header("⚙️ Ajustes")
        threshold = st.slider("Umbral de Limpieza (Alpha)", 0, 255, 128, 
                             help="Píxeles rojos = se eliminan. Píxeles sólidos = se quedan.")
        
        st.divider()
        st.header("🔍 Navegación")
        zoom_level = st.slider("Nivel de Zoom", 1.0, 10.0, 1.0, 0.5)
        
        st.divider()
        if st.button("🔄 Nueva Imagen"):
            reset_app()

    img_orig = Image.open(st.session_state.uploaded_file).convert("RGBA")
    
    data = img_orig.getdata()
    preview_data = []
    clean_data = []
    
    for item in data:
        r, g, b, a = item
        if 0 < a < threshold:
            preview_data.append((255, 0, 0, 255)) # Rojo en el visor
            clean_data.append((0, 0, 0, 0))       # Transparente en descarga
        elif a == 0:
            preview_data.append((0, 0, 0, 0))
            clean_data.append((0, 0, 0, 0))
        else:
            preview_data.append((r, g, b, 255))   # Sólido en visor
            clean_data.append((r, g, b, 255))     # Sólido en descarga

    img_preview = Image.new("RGBA", img_orig.size)
    img_preview.putdata(preview_data)
    
    img_final = Image.new("RGBA", img_orig.size)
    img_final.putdata(clean_data)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. ORIGINAL")
        st.image(img_orig, use_container_width=True)

    with col2:
        st.subheader("2. RESULTADO (Cuadro Negro)")
        
        buffered = io.BytesIO()
        img_preview.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Nota: Usamos doble llave {{ }} para que Python no se confunda con el código JS
        st.markdown(f"""
            <div id="view-wrapper" class="result-container">
                <div id="view-content" style="
                    width: 100%; 
                    height: 100%; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                ">
                    <img src="data:image/png;base64,{img_base64}" id="zoom-img" style="
                        transform: scale({zoom_level});
                        max-width: 100%;
                        height: auto;
                        user-select: none;
                        pointer-events: none;
                        transition: transform 0.1s ease-out;
                    " />
                </div>
            </div>

            <script>
                const wrapper = document.getElementById('view-wrapper');
                let isDragging = false;
                let startX, startY, scrollLeft, scrollTop;

                wrapper.addEventListener('mousedown', (e) => {{
                    isDragging = true;
                    startX = e.pageX - wrapper.offsetLeft;
                    startY = e.pageY - wrapper.offsetTop;
                    scrollLeft = wrapper.scrollLeft;
                    scrollTop = wrapper.scrollTop;
                }});

                wrapper.addEventListener('mouseleave', () => {{ isDragging = false; }});
                wrapper.addEventListener('mouseup', () => {{ isDragging = false; }});

                wrapper.addEventListener('mousemove', (e) => {{
                    if (!isDragging) return;
                    e.preventDefault();
                    const x = e.pageX - wrapper.offsetLeft;
                    const y = e.pageY - wrapper.offsetTop;
                    const walkX = (x - startX);
                    const walkY = (y - startY);
                    wrapper.scrollLeft = scrollLeft - walkX;
                    wrapper.scrollTop = scrollTop - walkY;
                }});
            </script>
            <style>
                #view-wrapper::-webkit-scrollbar {{ display: none; }}
                #view-wrapper {{ -ms-overflow-style: none; scrollbar-width: none; overflow: auto; }}
            </style>
        """, unsafe_allow_html=True)
        st.info("💡 Arrastra con el mouse dentro del cuadro negro para moverte cuando haya Zoom.")

    st.divider()
    buf_dl = io.BytesIO()
    img_final.save(buf_dl, format="PNG")
    
    st.download_button(
        label="💾 DESCARGAR PNG LIMPIO PARA DTF",
        data=buf_dl.getvalue(),
        file_name="dtf_listo_para_imprimir.png",
        mime="image/png",
        use_container_width=True
    )
