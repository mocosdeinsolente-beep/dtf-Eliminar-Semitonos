import streamlit as st
from PIL import Image
import io
import base64

st.set_page_config(page_title="Limpiador DTF Pro", layout="wide")

st.markdown("""
    <style>
    /* Estilo para el contenedor del resultado */
    .result-box {
        background-color: #000000;
        border: 2px solid #444;
        border-radius: 10px;
        height: 600px;
        width: 100%;
        overflow: hidden;
        position: relative;
        cursor: grab;
    }
    .result-box:active { cursor: grabbing; }
    #zoom-image {
        user-select: none;
        -webkit-user-drag: none;
        display: block;
        transition: transform 0.1s ease-out;
        transform-origin: 0 0;
    }
    </style>
    """, unsafe_allow_html=True)

def restart():
    st.session_state.clear()
    st.rerun()

st.title("🧼 Inspector y Limpiador DTF")

if 'file' not in st.session_state:
    uploaded = st.file_uploader("Sube tu archivo PNG", type=["png"])
    if uploaded:
        st.session_state.file = uploaded
        st.rerun()
else:
    # Controles en la barra lateral
    with st.sidebar:
        st.header("⚙️ Configuración")
        threshold = st.slider("Umbral de Limpieza (Alpha)", 0, 255, 128, 
                             help="Lo que esté por debajo de este valor se marcará en ROJO y se eliminará.")
        
        st.divider()
        st.header("🔍 Visualización")
        zoom = st.slider("Nivel de Zoom", 1.0, 10.0, 1.0, 0.5)
        
        st.divider()
        if st.button("🔄 Nueva Imagen"):
            restart()

    img = Image.open(st.session_state.file).convert("RGBA")
    
    # Creamos dos versiones: una visual (con rojo) y una limpia (transparente)
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

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. ORIGINAL")
        st.image(img, use_container_width=True)

    with col2:
        st.subheader("2. RESULTADO (Fondo Negro)")
        
        # Convertimos la imagen de preview a Base64 para JS
        buffered = io.BytesIO()
        img_preview.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        # Usamos .format() para evitar conflictos con las llaves de JS
        html_code = """
        <div id="wrapper" class="result-box">
            <img src="data:image/png;base64,{raw_img}" id="zoom-image" 
                 style="transform: scale({z});">
        </div>

        <script>
            var container = document.getElementById('wrapper');
            var img = document.getElementById('zoom-image');
            var isDragging = false;
            var startX, startY, scrollLeft, scrollTop;

            container.addEventListener('mousedown', function(e) {{
                isDragging = true;
                startX = e.pageX - container.offsetLeft;
                startY = e.pageY - container.offsetTop;
                scrollLeft = container.scrollLeft;
                scrollTop = container.scrollTop;
            }});

            container.addEventListener('mouseleave', function() {{ isDragging = false; }});
            container.addEventListener('mouseup', function() {{ isDragging = false; }});

            container.addEventListener('mousemove', function(e) {{
                if (!isDragging) return;
                e.preventDefault();
                var x = e.pageX - container.offsetLeft;
                var y = e.pageY - container.offsetTop;
                var walkX = (x - startX);
                var walkY = (y - startY);
                container.scrollLeft = scrollLeft - walkX;
                container.scrollTop = scrollTop - walkY;
            }});
        </script>
        <style>
            /* Esconder barras de scroll pero permitir movimiento */
            #wrapper::-webkit-scrollbar {{ display: none; }}
            #wrapper {{ -ms-overflow-style: none; scrollbar-width: none; overflow: auto; }}
        </style>
        """.format(raw_img=img_base64, z=zoom)
        
        st.markdown(html_code, unsafe_allow_html=True)
        st.info("💡 Arrastra con el ratón dentro del cuadro negro para moverte.")

    st.divider()
    dl_buffer = io.BytesIO()
    img_final.save(dl_buffer, format="PNG")
    
    st.download_button(
        label="💾 DESCARGAR PNG LIMPIO (SIN ROJO)",
        data=dl_buffer.getvalue(),
        file_name="dtf_pro_limpio.png",
        mime="image/png",
        use_container_width=True
    )
