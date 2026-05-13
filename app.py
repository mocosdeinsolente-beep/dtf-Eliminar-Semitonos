import streamlit as st
from PIL import Image
import io
import base64

st.set_page_config(page_title="DTF Alpha Cleaner Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #000000; color: #ffffff; }
    header, [data-testid="stHeader"] { background-color: #000000 !important; }
    .stApp { background-color: #111; }
    section[data-testid="stSidebar"] { background-color: #1a1a1a !important; }
    h1, h2, h3, p { color: #eee !important; }
    .stSlider label { color: #fff !important; }
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
                             help="Píxeles rojos = se eliminan. Píxeles sólidos = se imprimen.")
        
        st.divider()
        st.header("🔍 Visualización")
        zoom_level = st.slider("Nivel de Zoom", 1.0, 8.0, 2.0, 0.5)
        
        st.divider()
        if st.button("🔄 Nueva Imagen"):
            reset_app()

    img_orig = Image.open(st.session_state.uploaded_file).convert("RGBA")
    
    # Generamos la versión de inspección (Rojo para semitonos)
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
        st.caption("Imagen tal cual se subió.")

    with col2:
        st.subheader("2. RESULTADO FINAL (Pre-visualización)")
        
        # Convertir a base64 para el componente interactivo
        buffered = io.BytesIO()
        img_preview.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Esto permite el click-and-drag (pan) y el zoom centrado
        st.markdown(f"""
            <div id="wrapper" style="
                width: 100%; 
                height: 500px; 
                background: #000; 
                border: 2px solid #444; 
                overflow: hidden; 
                position: relative; 
                cursor: grab;
                border-radius: 10px;
            ">
                <div id="container" style="
                    width: 100%; 
                    height: 100%; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center;
                    transition: transform 0.1s;
                ">
                    <img src="data:image/png;base64,{img_base64}" id="zoom-img" style="
                        transform: scale({zoom_level});
                        max-width: 100%;
                        height: auto;
                        user-select: none;
                        -webkit-user-drag: none;
                    " />
                </div>
            </div>

            <script>
                const wrapper = document.getElementById('wrapper');
                const container = document.getElementById('container');
                let isDragging = false;
                let startX, startY, scrollLeft, scrollTop;

                wrapper.addEventListener('mousedown', (e) => {{
                    isDragging = true;
                    wrapper.style.cursor = 'grabbing';
                    startX = e.pageX - wrapper.offsetLeft;
                    startY = e.pageY - wrapper.offsetTop;
                    scrollLeft = wrapper.scrollLeft;
                    scrollTop = wrapper.scrollTop;
                }});

                wrapper.addEventListener('mouseleave', () => {{ isDragging = false; wrapper.style.cursor = 'grab'; }});
                wrapper.addEventListener('mouseup', () => {{ isDragging = false; wrapper.style.cursor = 'grab'; }});

                wrapper.addEventListener('mousemove', (e) => {{
                    if (!isDragging) return;
                    e.preventDefault();
                    const x = e.pageX - wrapper.offsetLeft;
                    const y = e.pageY - wrapper.offsetTop;
                    const walkX = (x - startX); 
                    const walkY = (y - startY);
                    wrapper.scrollLeft = scrollLeft - walkX;
                    wrapper.scrollTop = scrollTop - walkY;
                    container.style.transform = `translate(${{walkX}}px, ${{walkY}}px)`;
                }});
            </script>
            <style>
                #wrapper::-webkit-scrollbar {{ display: none; }}
                #wrapper {{ -ms-overflow-style: none; scrollbar-width: none; }}
            </style>
        """, unsafe_allow_html=True)
        st.info("💡 Haz clic y arrastra sobre la imagen negra para navegar por los detalles.")

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
