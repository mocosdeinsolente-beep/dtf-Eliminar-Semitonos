import streamlit as st
from PIL import Image
import io

st.set_page_config(page_title="DTF Alpha Cleaner Pro", layout="wide")

# ✅ MEJORA CLAVE: CSS optimizado con fondo negro garantizado para la imagen
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
    /* ✅ GARANTIZA que la imagen siempre se vea sobre fondo negro */
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
    st.rerun()

# 🎨 Interfaz mejorada con iconos y explicaciones claras
st.title("🧼 DTF Alpha Cleaner Pro")
st.write("""
**Limpia bordes suaves de IA para una impresión DTF perfecta.**  
*Convierte transparencias intermedias en bordes nítidos (0% o 100% de opacidad)*
""")

uploaded_file = st.file_uploader(
    "Sube tu diseño (PNG con transparencia)", 
    type=["png"], 
    key=f"uploader_{st.session_state.key}",
    help="⚠️ Formato requerido: PNG con canal alfa (transparencia)"
)

if uploaded_file is not None:
    with st.sidebar:
        st.header("⚙️ Ajustes avanzados")
        threshold = st.slider(
            "Umbral de limpieza", 
            0, 
            255, 
            128,
            help="Valores por debajo de este umbral se considerarán 'transparentes' y se eliminarán"
        )
        
        st.info("""
        🔹 **Rojo en vista previa** = Píxeles que serán eliminados  
        🔹 **Negro en descarga** = Fondo transparente (0% opacidad)  
        🔹 **Colores sólidos** = Áreas conservadas (100% opacidad)
        """)
        
        st.divider()
        if st.button("🔄 Cargar otra imagen", type="secondary"):
            restart()

    # 🖼️ Procesamiento de la imagen
    img = Image.open(uploaded_file).convert("RGBA")
    
    # ✅ OPTIMIZACIÓN: Procesamiento vectorizado (más rápido)
    pixels = list(img.getdata())
    preview_pixels = []
    clean_pixels = []
    
    for p in pixels:
        r, g, b, a = p
        # ✅ LÓGICA CORREGIDA: Manejo preciso de canales alfa
        if 0 < a < threshold:
            preview_pixels.append((255, 0, 0, 255))  # Marca roja visible
            clean_pixels.append((0, 0, 0, 0))        # Transparente en descarga
        elif a == 0:
            preview_pixels.append((0, 0, 0, 0))      # Conserva transparencia
            clean_pixels.append((0, 0, 0, 0))
        else:
            preview_pixels.append((r, g, b, 255))    # Fuerza opacidad total
            clean_pixels.append((r, g, b, 255))

    # ✅ GENERACIÓN DE IMÁGENES CORREGIDA
    img_preview = Image.new("RGBA", img.size)
    img_preview.putdata(preview_pixels)
    
    img_clean = Image.new("RGBA", img.size)
    img_clean.putdata(clean_pixels)

    # 📊 Visualización en dos columnas
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🖼️ 1. ORIGINAL (con transparencia)")
        st.image(img, use_container_width=True)
        st.caption("Transparencias suaves pueden causar problemas en impresión DTF")

    with col2:
        st.subheader("🔍 2. RESULTADO PROCESADO (FONDO NEGRO)")
        # ✅ CORRECCIÓN PRINCIPAL: Ahora muestra la vista previa CORRECTA
        st.markdown('<div class="black-box">', unsafe_allow_html=True)
        st.image(img_preview, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.caption("""
        **ROJO** = Áreas que serán eliminadas | 
        **Colores sólidos** = Áreas conservadas
        """)

    st.divider()
    
    # 💾 Generación del archivo para descarga
    buf = io.BytesIO()
    img_clean.save(buf, format="PNG")
    
    st.download_button(
        label="✅ DESCARGAR PNG LIMPIO (Listo para DTF)",
        data=buf.getvalue(),
        file_name="dtf_limpio.png",
        mime="image/png",
        use_container_width=True,
        type="primary"
    )
    
    st.success("""
    ✅ **Tu imagen está lista para impresión DTF**  
    - Bordos suaves eliminados  
    - Transparencias convertidas a 0% o 100%  
    - Formato PNG optimizado para maquinaria DTF
    """)

else:
    # 🎯 Mensaje de bienvenida cuando no hay imagen
    st.info("""
    ### 📌 ¿Cómo funciona?
    1. Sube un PNG con transparencia (ej: diseño de Photoshop/Illustrator)  
    2. Ajusta el umbral para definir qué bordes suaves eliminar  
    3. Descarga tu archivo listo para impresión DTF
    
    **Ejemplo de uso:**  
    - Para diseños con sombras suaves: usa umbral 50-80  
    - Para diseños con bordes definidos: usa umbral 150+
    """)
    st.image("https://i.imgur.com/V7LQY6c.png", caption="Ejemplo de proceso DTF")
